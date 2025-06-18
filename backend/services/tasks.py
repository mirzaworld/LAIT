from celery import Celery
import os
from services.s3_service import S3Service
from services.pdf_parser_service import PDFParserService
from ml.train_outlier_model import predict_anomalies
from ml.train_overspend_model import predict_overspend
from ml.train_vendor_cluster import predict_vendor_cluster
import logging

# Initialize Celery
celery_app = Celery('tasks', broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

# Initialize services
s3_service = S3Service()
pdf_parser = PDFParserService()

@celery_app.task
def process_invoice(file_key, invoice_id):
    """Process an uploaded invoice PDF."""
    try:
        # Get the file from S3
        pdf_file = s3_service.get_file(file_key)
        
        # Parse the PDF
        invoice_data = pdf_parser.parse_invoice(pdf_file)
        
        # Update invoice record with parsed data
        # This would typically update the database with extracted metadata
        
        # Process line items for anomalies
        line_items = invoice_data.get('line_items', [])
        if line_items:
            anomalies, scores = predict_anomalies(line_items)
            
            # Update line items with anomaly flags
            for item, is_anomaly, score in zip(line_items, anomalies, scores):
                item['is_flagged'] = is_anomaly
                item['anomaly_score'] = score
        
        # Predict potential overspend
        overspend_amount = predict_overspend(invoice_data, line_items)
        
        # Update the invoice record with predictions
        # This would update the database with results
        
        return {
            'success': True,
            'invoice_id': invoice_id,
            'anomalies_found': sum(anomalies) if line_items else 0,
            'overspend_prediction': overspend_amount
        }
        
    except Exception as e:
        logging.error(f"Error processing invoice {invoice_id}: {str(e)}")
        return {
            'success': False,
            'invoice_id': invoice_id,
            'error': str(e)
        }

@celery_app.task
def retrain_models():
    """Retrain all ML models with current data."""
    try:
        # Import training functions
        from ml.train_outlier_model import train_outlier_model
        from ml.train_overspend_model import train_overspend_model
        from ml.train_vendor_cluster import train_vendor_cluster_model
        
        # Get current data from database
        # This would typically query the database for all invoice and line item data
        
        # Train models
        train_outlier_model()
        train_overspend_model()
        train_vendor_cluster_model()
        
        return {
            'success': True,
            'message': 'All models retrained successfully'
        }
        
    except Exception as e:
        logging.error(f"Error retraining models: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@celery_app.task
def cleanup_old_files():
    """Clean up old temporary files and processed PDFs."""
    try:
        # Get list of old files
        # This would typically check a database for files older than X days
        
        # Delete files from S3
        # s3_service.delete_file(key) for each old file
        
        return {
            'success': True,
            'message': 'Old files cleaned up successfully'
        }
        
    except Exception as e:
        logging.error(f"Error cleaning up files: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
