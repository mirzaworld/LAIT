"""Machine Learning related routes"""
from flask import jsonify, request, current_app as app

def register_ml_routes(app):
    """Register ML-related routes"""
    
    @app.route('/api/ml/test')
    def ml_test():
        """Test ML model functionality"""
        return jsonify({
            "status": "ML Models Active",
            "models": {
                "risk_predictor": app.risk_predictor is not None,
                "vendor_analyzer": app.vendor_analyzer is not None,
                "invoice_analyzer": app.invoice_analyzer is not None,
                "matter_analyzer": app.matter_analyzer is not None,
                "enhanced_invoice_analyzer": app.enhanced_invoice_analyzer is not None
            },
            "capabilities": {
                "invoice_analysis": True,
                "predictive_analytics": True,
                "anomaly_detection": True,
                "vendor_clustering": True
            }
        })
    
    @app.route('/api/ml/invoice-analysis', methods=['POST'])
    def analyze_invoice_ml():
        """Advanced AI invoice analysis with validation"""
        try:
            data = request.get_json()
            
            if not app.invoice_analyzer:
                return jsonify({"error": "Invoice analyzer not available"}), 503
                
            analysis = app.invoice_analyzer.analyze_invoice(data)
            return jsonify(analysis)
            
        except Exception as e:
            app.logger.error(f"Error analyzing invoice: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/ml/anomaly-detection', methods=['POST'])
    def detect_anomalies():
        """ML-powered anomaly detection"""
        try:
            data = request.get_json()
            invoices = data.get('invoices', [])
            
            if not app.enhanced_invoice_analyzer:
                return jsonify({"error": "Enhanced invoice analyzer not available"}), 503
                
            anomalies = app.enhanced_invoice_analyzer.detect_anomalies(invoices)
            return jsonify({"anomalies": anomalies})
            
        except Exception as e:
            app.logger.error(f"Error detecting anomalies: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/ml/budget-forecast', methods=['POST'])
    def budget_forecast():
        """Predictive analytics for budget forecasting"""
        try:
            data = request.get_json()
            matter_id = data.get('matter_id')
            timeframe = data.get('timeframe', 12)  # months
            
            if not matter_id:
                return jsonify({"error": "Matter ID required"}), 400
                
            if not app.matter_analyzer:
                return jsonify({"error": "Matter analyzer not available"}), 503
                
            forecast = app.matter_analyzer.forecast_budget(matter_id, timeframe)
            return jsonify(forecast)
            
        except Exception as e:
            app.logger.error(f"Error forecasting budget: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/ml/vendor-analysis/<vendor_name>')
    def vendor_analysis(vendor_name):
        """Enhanced vendor analysis"""
        try:
            if not app.vendor_analyzer:
                return jsonify({"error": "Vendor analyzer not available"}), 503
                
            analysis = app.vendor_analyzer.analyze_vendor(vendor_name)
            return jsonify(analysis)
            
        except Exception as e:
            app.logger.error(f"Error analyzing vendor {vendor_name}: {e}")
            return jsonify({"error": str(e)}), 500
