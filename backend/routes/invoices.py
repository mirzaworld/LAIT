"""
Invoice routes: upload, list, get, file download
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Invoice, InvoiceLine
from ..services.s3_service import S3Service
from ..services.pdf_parser_service import PDFParserService
import tempfile

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

@invoices_bp.route('', methods=['POST'])
@jwt_required()
def upload_invoice():
    if 'file' not in request.files:
        return jsonify({'msg': 'No file uploaded'}), 400
    file = request.files['file']
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'msg': 'Only PDF files allowed'}), 400
    s3 = S3Service()
    key = s3.upload_file(file)
    # Save file temporarily for parsing
    file.seek(0)
    with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
        file.save(tmp.name)
        parser = PDFParserService()
        invoice_data = parser.parse_invoice(tmp.name)
    # TODO: Save invoice_data to DB, trigger ML, etc.
    return jsonify({'msg': 'Invoice uploaded', 's3_key': key, 'parsed': invoice_data})
