"""
Invoice routes: upload, list, get, file download
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Invoice, InvoiceLine
from ..services.s3_service import S3Service
from ..services.pdf_parser_service import PDFParserService
import tempfile
import os

invoices_bp = Blueprint('invoices', __name__, url_prefix='/api/invoices')

@invoices_bp.route('', methods=['GET'])
@jwt_required()
def list_invoices():
    invoices = Invoice.query.all()
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

@invoices_bp.route('/<int:invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    inv = Invoice.query.get_or_404(invoice_id)
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

@invoices_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_invoice():
    """Upload a new invoice (PDF) and save parsed data to the database"""
    user_id = get_jwt_identity()
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
    invoice = Invoice(
        vendor_name=parsed_data['vendor_name'],
        invoice_number=parsed_data['invoice_number'],
        date=parsed_data['date'],
        total_amount=parsed_data['total_amount'],
        overspend_risk=parsed_data['overspend_risk'],
        processed=True,
        pdf_s3_key=parsed_data['pdf_s3_key']
    )
    db.session.add(invoice)
    db.session.commit()

    # Clean up temporary file
    os.remove(temp_file_path)

    return jsonify({'message': 'Invoice uploaded successfully', 'invoice_id': invoice.id}), 201

@invoices_bp.route('/download/<int:invoice_id>', methods=['GET'])
@jwt_required()
def download_invoice(invoice_id):
    """Download invoice PDF from S3"""
    inv = Invoice.query.get_or_404(invoice_id)
    s3 = S3Service()
    file_url = s3.generate_presigned_url(inv.pdf_s3_key) if inv.pdf_s3_key else None

    if not file_url:
        return jsonify({'message': 'File not found'}), 404

    return jsonify({'file_url': file_url})
