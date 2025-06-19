"""
Invoice routes: upload, list, get, file download
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.db.database import get_db_session
from backend.models.db_models import Invoice as DbInvoice
from backend.services.s3_service import S3Service
from backend.services.pdf_parser_service import PDFParserService
import tempfile
import os

invoices_bp = Blueprint('invoices', __name__, url_prefix='/api/invoices')

@invoices_bp.route('', methods=['GET'])
@jwt_required()
def list_invoices():
    current_user = get_jwt_identity()
    session = get_db_session()
    try:
        invoices = session.query(DbInvoice).all()
        result = []
        for inv in invoices:
            result.append({
                'id': inv.id,
                'vendor_name': inv.vendor_name,
                'invoice_number': inv.invoice_number,
                'date': inv.date.isoformat() if inv.date else None,
                'total_amount': inv.total_amount,
                'overspend_risk': inv.overspend_risk,
                'processed': inv.processed,
                'pdf_s3_key': inv.pdf_s3_key
            })
        return jsonify(result)
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
        lines = [
            {
                'id': l.id,
                'description': l.description,
                'hours': l.hours,
                'rate': l.rate,
                'line_total': l.line_total,
                'is_flagged': l.is_flagged,
                'flag_reason': l.flag_reason
            } for l in inv.lines
        ]
        return jsonify({
            'id': inv.id,
            'vendor_name': inv.vendor_name,
            'invoice_number': inv.invoice_number,
            'date': inv.date.isoformat() if inv.date else None,
            'total_amount': inv.total_amount,
            'overspend_risk': inv.overspend_risk,
            'processed': inv.processed,
            'pdf_url': file_url,
            'lines': lines
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@invoices_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_invoice():
    """Upload a new invoice (PDF) and save parsed data to the database"""
    current_user = get_jwt_identity()
    user_id = current_user.id
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file.save(temp_file.name)
        temp_file_path = temp_file.name

    # Parse PDF
    parser = PDFParserService()
    parsed_data = parser.parse_pdf(temp_file_path)

    # Save to database
    session = get_db_session()
    try:
        invoice = DbInvoice(
            vendor_name=parsed_data['vendor_name'],
            invoice_number=parsed_data['invoice_number'],
            date=parsed_data['date'],
            total_amount=parsed_data['total_amount'],
            overspend_risk=parsed_data['overspend_risk'],
            processed=True,
            pdf_s3_key=parsed_data['pdf_s3_key']
        )
        session.add(invoice)
        session.commit()
        invoice_id = invoice.id  # Store ID before closing session
        session.close()
        
        # Clean up temporary file
        os.remove(temp_file_path)
        
        return jsonify({'message': 'Invoice uploaded successfully', 'invoice_id': invoice_id})
    except Exception as e:
        session.rollback()
        # Clean up temporary file even if there's an error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return jsonify({'message': f'Error processing invoice: {str(e)}'}), 500
    finally:
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
