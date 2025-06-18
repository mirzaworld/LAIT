from celery_worker import celery
from models.invoice_analyzer import InvoiceAnalyzer
from models.risk_predictor import RiskPredictor
from models.vendor_analyzer import VendorAnalyzer
from db.database import get_db_session, Invoice, Vendor, RiskFactor
from services.notification_service import NotificationService
import time
import os
import logging
from datetime import datetime, timedelta
import io
import boto3
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
invoice_analyzer = InvoiceAnalyzer()
risk_predictor = RiskPredictor()
vendor_analyzer = VendorAnalyzer()
notification_service = NotificationService()

@celery.task(name="tasks.process_invoice")
def process_invoice(invoice_id):
    """
    Process and analyze a new invoice
    """
    session = get_db_session()
    try:
        # Fetch invoice data
        invoice = session.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            logger.error(f"Invoice with ID {invoice_id} not found")
            return {"status": "error", "message": "Invoice not found"}
        
        # Analyze invoice
        analysis_result = invoice_analyzer.analyze_invoice(invoice)
        
        # Update invoice with analysis results
        invoice.risk_score = analysis_result.get('risk_score', 0)
        invoice.analysis_result = analysis_result
        
        # Create risk factors
        if 'anomalies' in analysis_result:
            for anomaly in analysis_result['anomalies']:
                risk_factor = RiskFactor(
                    invoice_id=invoice.id,
                    factor_type=anomaly.get('type', 'unknown'),
                    description=anomaly.get('description', ''),
                    severity=anomaly.get('severity', 'low'),
                    impact_score=anomaly.get('impact_score', 0.0)
                )
                session.add(risk_factor)
        
        # Send notification
        notification_service.send_notification(
            'invoice_analyzed',
            {
                'invoice_id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'risk_score': invoice.risk_score,
                'vendor_name': invoice.vendor.name if invoice.vendor else 'Unknown',
                'anomalies_count': len(analysis_result.get('anomalies', [])),
                'amount': invoice.amount
            }
        )
        
        session.commit()
        return {"status": "success", "invoice_id": invoice_id}
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error processing invoice {invoice_id}: {str(e)}")
        return {"status": "error", "message": str(e)}
    
    finally:
        session.close()

@celery.task(name="tasks.retrain_models")
def retrain_models():
    """
    Periodically retrain ML models with new data
    """
    try:
        # Retrain invoice anomaly detection model
        invoice_analyzer.retrain_model()
        
        # Retrain risk prediction model
        risk_predictor.retrain_model()
        
        # Retrain vendor clustering model
        vendor_analyzer.retrain_model()
        
        logger.info("All models successfully retrained")
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error retraining models: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery.task(name="tasks.upload_to_s3")
def upload_to_s3(file_path, object_name=None):
    """
    Upload a file to an S3 bucket
    """
    try:
        # If object_name not provided, use file_path's basename
        if object_name is None:
            object_name = os.path.basename(file_path)
            
        # Get S3 bucket from config
        s3_bucket = os.getenv('S3_BUCKET', 'legalspend-invoices')
        
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        # Upload file
        s3_client.upload_file(file_path, s3_bucket, object_name)
        logger.info(f"File {file_path} uploaded to S3 bucket {s3_bucket} as {object_name}")
        
        return {
            "status": "success", 
            "s3_path": f"s3://{s3_bucket}/{object_name}"
        }
        
    except Exception as e:
        logger.error(f"Error uploading file to S3: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery.task(name="tasks.process_invoice_batch")
def process_invoice_batch(invoice_ids):
    """
    Process a batch of invoices
    """
    results = []
    for invoice_id in invoice_ids:
        result = process_invoice(invoice_id)
        results.append({"invoice_id": invoice_id, "result": result})
    
    return {"status": "completed", "results": results}

@celery.task(name="tasks.generate_monthly_report")
def generate_monthly_report():
    """
    Generate monthly spending report
    """
    from services.report_service import ReportService
    
    try:
        # Create report service
        report_service = ReportService()
        
        # Generate report data
        report_data = report_service.generate_monthly_report()
        
        # Create PDF report
        pdf_content = report_service.generate_pdf_report(report_data)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_content)
            tmp_path = tmp.name
        
        # Upload to S3
        date_str = datetime.now().strftime("%Y-%m")
        s3_path = f"reports/monthly_report_{date_str}.pdf"
        upload_result = upload_to_s3(tmp_path, s3_path)
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        # Send notification
        if upload_result.get("status") == "success":
            notification_service.send_notification(
                'report_generated',
                {
                    'report_type': 'monthly',
                    'report_date': date_str,
                    'report_url': upload_result.get('s3_path')
                }
            )
        
        return {
            "status": "success", 
            "report_path": upload_result.get('s3_path')
        }
        
    except Exception as e:
        logger.error(f"Error generating monthly report: {str(e)}")
        return {"status": "error", "message": str(e)}
