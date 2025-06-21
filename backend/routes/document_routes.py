"""Document-related routes"""
from flask import jsonify, request, current_app as app
from datetime import datetime
import time
import io
import base64

def register_document_routes(app):
    """Register document-related routes"""
    
    @app.route('/api/documents/upload', methods=['POST'])
    def upload_document():
        """Advanced document upload with AI classification"""
        try:
            data = request.get_json()
            
            # Extract document data
            doc_data = data.get('document', {})
            if not doc_data or 'content' not in doc_data:
                return jsonify({"error": "Document content required"}), 400
                
            # Process document if ML models are available
            if app.enhanced_invoice_analyzer:
                analysis = app.enhanced_invoice_analyzer.analyze_document(doc_data)
            else:
                analysis = {
                    "type": "unknown",
                    "confidence": 0,
                    "extracted_data": {}
                }
                
            # Generate response
            document_result = {
                "document_id": f"DOC-{int(time.time())}",
                "status": "processed",
                "analysis": analysis,
                "metadata": {
                    "upload_timestamp": datetime.now().isoformat(),
                    "file_type": doc_data.get('type', 'unknown'),
                    "size": len(doc_data.get('content', '')),
                    "processed": True
                }
            }
            
            return jsonify(document_result)
            
        except Exception as e:
            app.logger.error(f"Error uploading document: {e}")
            return jsonify({"error": "Upload failed"}), 500
    
    @app.route('/api/documents/search', methods=['POST'])
    def search_documents():
        """Advanced document search with NLP processing"""
        try:
            data = request.get_json()
            query = data.get('query', '')
            filters = data.get('filters', {})
            
            if not query:
                return jsonify({"error": "Search query required"}), 400
                
            # Perform document search
            # This would normally use an actual search engine like Elasticsearch
            documents = []  # Placeholder for search results
            
            return jsonify({
                "query": query,
                "result_count": len(documents),
                "documents": documents
            })
            
        except Exception as e:
            app.logger.error(f"Document search error: {e}")
            return jsonify({"error": str(e)}), 500
            
    @app.route('/api/documents/analyze', methods=['POST'])
    def analyze_document():
        """Analyze document for key information"""
        try:
            data = request.get_json()
            doc_id = data.get('document_id')
            
            if not doc_id:
                return jsonify({"error": "Document ID required"}), 400
                
            # Perform document analysis
            if app.enhanced_invoice_analyzer:
                analysis = app.enhanced_invoice_analyzer.analyze_document_by_id(doc_id)
                return jsonify(analysis)
            else:
                return jsonify({"error": "Document analyzer not available"}), 503
                
        except Exception as e:
            app.logger.error(f"Document analysis error: {e}")
            return jsonify({"error": str(e)}), 500
