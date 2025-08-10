"""
Invoice routes: upload, list, get, file download
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from db.database import get_db_session, Invoice as DbInvoice, LineItem, Vendor
from services.s3_service import S3Service
from services.pdf_parser_service import PDFParserService
import tempfile
import os
from datetime import datetime

invoices_bp = Blueprint('invoices', __name__, url_prefix='/api/invoices')

@invoices_bp.route('', methods=['GET'])
@jwt_required()
def list_invoices():
    session = get_db_session()
    try:
        invoices = session.query(DbInvoice).all()
        
        # If no invoices in database, return demo data
        if not invoices:
            demo_invoices = [
                {
                    'id': 'INV-2024-001',
                    'vendor': 'Morrison & Foerster LLP',
                    'amount': 45750,
                    'status': 'approved',
                    'date': '2024-01-15',
                    'dueDate': '2024-02-14',
                    'matter': 'IP Litigation - TechCorp vs CompetitorX',
                    'riskScore': 15,
                    'category': 'Litigation',
                    'description': 'Discovery and motion practice for Q4 2024',
                    'hours': 52.5,
                    'rate': 950,
                    'total': 45750
                },
                {
                    'id': 'INV-2024-002',
                    'vendor': 'Baker McKenzie',
                    'amount': 23400,
                    'status': 'pending',
                    'date': '2024-01-14',
                    'dueDate': '2024-02-13',
                    'matter': 'M&A Advisory - Acquisition of StartupY',
                    'riskScore': 45,
                    'category': 'Corporate',
                    'description': 'Due diligence and transaction documentation',
                    'hours': 28.2,
                    'rate': 850,
                    'total': 23400
                },
                {
                    'id': 'INV-2024-003',
                    'vendor': 'Latham & Watkins',
                    'amount': 67800,
                    'status': 'flagged',
                    'date': '2024-01-13',
                    'dueDate': '2024-02-12',
                    'matter': 'Regulatory Compliance - FDA Approval',
                    'riskScore': 85,
                    'category': 'Regulatory',
                    'description': '340% increase from previous billing period',
                    'hours': 61.6,
                    'rate': 1100,
                    'total': 67800
                },
                {
                    'id': 'INV-2024-004',
                    'vendor': 'Skadden Arps',
                    'amount': 32500,
                    'status': 'processing',
                    'date': '2024-01-12',
                    'dueDate': '2024-02-11',
                    'matter': 'Employment Dispute Resolution',
                    'riskScore': 28,
                    'category': 'Employment',
                    'description': 'Settlement negotiations and documentation',
                    'hours': 31.0,
                    'rate': 1050,
                    'total': 32500
                },
                {
                    'id': 'INV-2024-005',
                    'vendor': 'White & Case',
                    'amount': 18900,
                    'status': 'approved',
                    'date': '2024-01-11',
                    'dueDate': '2024-02-10',
                    'matter': 'Contract Negotiation - Software License',
                    'riskScore': 12,
                    'category': 'IP',
                    'description': 'Software licensing agreement review and negotiation',
                    'hours': 21.0,
                    'rate': 900,
                    'total': 18900
                }
            ]
            return jsonify({'invoices': demo_invoices})
        result = []
        for inv in invoices:
            result.append({
                'id': inv.id,
                'vendor_name': inv.vendor.name if inv.vendor else 'Unknown Vendor',
                'invoice_number': inv.invoice_number,
                'date': inv.date.isoformat() if inv.date else None,
                'total_amount': inv.amount,
                'risk_score': inv.risk_score,
                'overspend_risk': inv.overspend_risk,
                'processed': inv.processed,
                'pdf_s3_key': inv.pdf_s3_key
            })
        return jsonify({'invoices': result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@invoices_bp.route('/<int:invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    current_user = get_jwt_identity()
    session = get_db_session()
    try:
        inv = session.query(DbInvoice).filter_by(id=invoice_id).first()
        if not inv:
            return jsonify({"error": "Invoice not found"}), 404
            
        s3 = S3Service()
        file_url = s3.generate_presigned_url(inv.pdf_s3_key) if inv.pdf_s3_key else None
        # Fix relationship attribute (line_items instead of lines)
        lines = [
            {
                'id': l.id,
                'description': l.description,
                'hours': l.hours,
                'rate': l.rate,
                'amount': l.amount,
                'is_flagged': l.is_flagged,
                'flag_reason': l.flag_reason
            } for l in inv.line_items
        ]
        return jsonify({
            'id': inv.id,
            'vendor_name': inv.vendor.name if inv.vendor else 'Unknown Vendor',
            'invoice_number': inv.invoice_number,
            'date': inv.date.isoformat() if inv.date else None,
            'total_amount': inv.amount,
            'risk_score': inv.risk_score,
            'overspend_risk': inv.overspend_risk,
            'processed': inv.processed,
            'pdf_url': file_url,
            'analysis_result': inv.analysis_result,
            'lines': lines
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@invoices_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_invoice():
    """Upload a new invoice (PDF) and save parsed data to the database with ML analysis"""
    user_id = get_jwt_identity()
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    parser = PDFParserService()
    s3 = S3Service()
    temp_file_path = None
    session = get_db_session()
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
        parsed_data = parser.parse_pdf(temp_file_path)
        pdf_s3_key = None
        try:
            if os.getenv('AWS_S3_BUCKET'):
                with open(temp_file_path, 'rb') as fobj:
                    from werkzeug.datastructures import FileStorage
                    fobj_seek = FileStorage(stream=fobj, filename=file.filename, content_type='application/pdf')
                    pdf_s3_key = s3.upload_file(fobj_seek)
        except Exception:
            pdf_s3_key = None
        vendor_name = parsed_data.get('vendor_name') or 'Unknown Vendor'
        vendor = session.query(Vendor).filter_by(name=vendor_name).first()
        if not vendor:
            vendor = Vendor(name=vendor_name, status='active')
            session.add(vendor)
            session.flush()
        date_val = None
        raw_date = parsed_data.get('date')
        if raw_date:
            try:
                date_val = datetime.strptime(raw_date, '%Y-%m-%d')
            except ValueError:
                try:
                    date_val = datetime.fromisoformat(raw_date)
                except Exception:
                    date_val = datetime.utcnow()
        total_amount = parsed_data.get('total_amount') or parsed_data.get('amount') or 0
        # ML Analysis integration
        risk_score = None
        analysis_result = None
        try:
            analyzer = getattr(current_app, 'invoice_analyzer', None)
            if analyzer:
                # Build minimal structure expected by analyzer
                invoice_input = {
                    'amount': total_amount,
                    'line_items': parsed_data.get('line_items', []),
                    'description': parsed_data.get('description'),
                    'vendor_name': vendor_name
                }
                analysis_result = analyzer.analyze_invoice(invoice_input)
                risk_score = analysis_result.get('risk_score') or analysis_result.get('risk', {}).get('score')
        except Exception as ml_e:
            current_app.logger.warning(f"Invoice ML analysis failed: {ml_e}")
        # Fallback risk scoring
        if risk_score is None:
            risk_score = min(100, (float(total_amount) / 1000.0)) if total_amount else 0
        invoice = DbInvoice(
            vendor_id=vendor.id,
            invoice_number=parsed_data.get('invoice_number'),
            date=date_val or datetime.utcnow(),
            amount=total_amount,
            overspend_risk=(float(risk_score) / 100.0) if risk_score else 0,
            processed=True,
            pdf_s3_key=pdf_s3_key,
            uploaded_by=user_id,
            status='uploaded',
            risk_score=risk_score,
            analysis_result=analysis_result
        )
        session.add(invoice)
        session.flush()
        for li in parsed_data.get('line_items', []):
            line = LineItem(
                invoice_id=invoice.id,
                description=li.get('description'),
                hours=li.get('hours'),
                rate=li.get('rate'),
                amount=li.get('amount')
            )
            session.add(line)
        session.commit()
        return jsonify({'message': 'Invoice uploaded successfully', 'invoice_id': invoice.id, 'risk_score': risk_score})
    except Exception as e:
        session.rollback()
        return jsonify({'message': f'Error processing invoice: {str(e)}'}), 500
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        session.close()

@invoices_bp.route('/download/<int:invoice_id>', methods=['GET'])
@jwt_required()
def download_invoice(invoice_id):
    """Download invoice PDF from S3"""
    current_user = get_jwt_identity()
    session = get_db_session()
    try:
        inv = session.query(DbInvoice).filter_by(id=invoice_id).first()
        if not inv:
            return jsonify({"error": "Invoice not found"}), 404
            
        s3 = S3Service()
        file_url = s3.generate_presigned_url(inv.pdf_s3_key) if inv.pdf_s3_key else None
        
        if not file_url:
            return jsonify({'message': 'File not found'}), 404
            
        return jsonify({'file_url': file_url})
    except Exception as e:
        return jsonify({'message': f'Error retrieving invoice: {str(e)}'}), 500
    finally:
        session.close()
