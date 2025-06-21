"""
Enhanced Invoice Upload Route
Uses real trained ML models for PDF analysis
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.enhanced_pdf_upload_service import EnhancedPDFUploadService
from dev_auth import development_jwt_required
import logging

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__, url_prefix='/api')

@upload_bp.route('/upload-invoice', methods=['POST'])
def upload_invoice():
    """Enhanced invoice upload with real ML analysis"""
    try:
        logger.info("Processing invoice upload request")
        
        # Initialize upload service
        upload_service = EnhancedPDFUploadService()
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Get additional form data
            additional_data = {
                'vendor': request.form.get('vendor'),
                'amount': request.form.get('amount'),
                'date': request.form.get('date'),
                'category': request.form.get('category'),
                'description': request.form.get('description')
            }
            
            # Process the file
            result = upload_service.process_uploaded_file(file, additional_data)
            
            logger.info(f"Upload processing completed: {result.get('success', False)}")
            return jsonify(result)
            
        else:
            # Handle JSON data (for testing without actual file)
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No file or data provided'}), 400
            
            # Create mock result for testing
            result = {
                'success': True,
                'invoice_id': f"TEST-{data.get('vendor', 'UNKNOWN')}",
                'invoice_added': True,
                'invoice_data': {
                    'vendor': data.get('vendor', 'Test Vendor'),
                    'amount': float(data.get('amount', 1000)),
                    'date': data.get('date', '2024-01-15'),
                    'invoice_number': 'TEST-001',
                    'line_items_count': 3,
                    'total_hours': 10.5,
                    'practice_areas': ['General']
                },
                'analysis': {
                    'risk_score': 35,
                    'risk_level': 'medium',
                    'recommendations': [
                        'Review billing rates for compliance',
                        'Validate timekeeper allocations'
                    ],
                    'anomalies': [],
                    'insights': [
                        'Standard billing pattern detected',
                        'Rates within market range'
                    ],
                    'market_analysis': {
                        'position': 'market_rate',
                        'average_rate': 450,
                        'outlier_count': 0
                    }
                },
                'extraction_results': {
                    'text_extracted': True,
                    'tables_found': 1,
                    'line_items_extracted': 3,
                    'confidence_score': 0.85
                }
            }
            
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"Error in upload-invoice endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}',
            'invoice_added': False
        }), 500

@upload_bp.route('/upload-invoice/analyze', methods=['POST'])
@development_jwt_required
def analyze_uploaded_invoice():
    """Analyze an uploaded invoice without saving"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Initialize upload service
        upload_service = EnhancedPDFUploadService()
        
        # Process file for analysis only
        result = upload_service.process_uploaded_file(file)
        
        # Return analysis results
        analysis_result = {
            'analysis_completed': result.get('success', False),
            'extraction_confidence': result.get('extraction_results', {}).get('confidence_score', 0),
            'risk_assessment': result.get('analysis', {}),
            'invoice_preview': result.get('invoice_data', {}),
            'ml_insights': result.get('analysis', {}).get('insights', [])
        }
        
        return jsonify(analysis_result)
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500
