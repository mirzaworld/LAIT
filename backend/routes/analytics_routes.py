"""Analytics-related routes"""
from flask import jsonify, request, current_app as app
from datetime import datetime

def register_analytics_routes(app):
    """Register analytics-related routes"""
    
    @app.route('/api/analytics/spend-trends')
    def get_spend_trends():
        """Comprehensive spend trend analysis"""
        try:
            db = app.extensions['sqlalchemy'].db
            invoices = db.session.query(app.models.Invoice).all()
            
            # Group invoices by date and calculate metrics
            trends = {}
            for invoice in invoices:
                month = invoice.date.strftime('%Y-%m')
                if month not in trends:
                    trends[month] = {
                        'period': month,
                        'total_spend': 0,
                        'invoice_count': 0,
                        'vendors': set(),
                        'categories': {}
                    }
                    
                trends[month]['total_spend'] += invoice.amount
                trends[month]['invoice_count'] += 1
                trends[month]['vendors'].add(invoice.vendor)
                
                # Track spend by category
                cat = invoice.category
                if cat not in trends[month]['categories']:
                    trends[month]['categories'][cat] = 0
                trends[month]['categories'][cat] += invoice.amount
            
            # Format results
            trend_list = []
            for month, data in sorted(trends.items()):
                data['vendor_count'] = len(data['vendors'])
                data['vendors'] = list(data['vendors'])  # Convert set to list for JSON
                trend_list.append(data)
                
            return jsonify(trend_list)
            
        except Exception as e:
            app.logger.error(f"Error fetching spend trends: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/analytics/vendor-performance')
    def vendor_performance():
        """Analyze vendor performance metrics"""
        try:
            db = app.extensions['sqlalchemy'].db
            invoices = db.session.query(app.models.Invoice).all()
            
            vendor_metrics = {}
            for invoice in invoices:
                if invoice.vendor not in vendor_metrics:
                    vendor_metrics[invoice.vendor] = {
                        'vendor': invoice.vendor,
                        'total_spend': 0,
                        'invoice_count': 0,
                        'average_amount': 0,
                        'risk_scores': [],
                        'categories': {}
                    }
                    
                vm = vendor_metrics[invoice.vendor]
                vm['total_spend'] += invoice.amount
                vm['invoice_count'] += 1
                vm['risk_scores'].append(invoice.risk_score)
                
                if invoice.category not in vm['categories']:
                    vm['categories'][invoice.category] = 0
                vm['categories'][invoice.category] += invoice.amount
            
            # Calculate final metrics
            performance = []
            for vendor, metrics in vendor_metrics.items():
                metrics['average_amount'] = metrics['total_spend'] / metrics['invoice_count']
                metrics['average_risk_score'] = sum(metrics['risk_scores']) / len(metrics['risk_scores'])
                del metrics['risk_scores']  # Remove raw scores
                performance.append(metrics)
                
            return jsonify(performance)
            
        except Exception as e:
            app.logger.error(f"Error analyzing vendor performance: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/analytics/budget-forecast')
    def get_budget_forecast():
        """Get budget forecast based on historical data"""
        try:
            if not app.matter_analyzer:
                return jsonify({"error": "Matter analyzer not available"}), 503
                
            # Get parameters
            months = int(request.args.get('months', 12))
            categories = request.args.getlist('categories')
            
            forecast = app.matter_analyzer.generate_budget_forecast(months, categories)
            return jsonify(forecast)
            
        except Exception as e:
            app.logger.error(f"Error generating budget forecast: {e}")
            return jsonify({"error": str(e)}), 500
            
    @app.route('/api/analytics/dashboard/metrics')
    def get_dashboard_metrics():
        """Enhanced dashboard metrics"""
        try:
            db = app.extensions['sqlalchemy'].db
            invoices = db.session.query(app.models.Invoice).all()
            
            # Calculate basic metrics
            total_spend = sum(inv.amount for inv in invoices)
            vendors = {inv.vendor for inv in invoices}
            categories = {inv.category for inv in invoices}
            
            # Calculate risk distribution
            risk_levels = {
                'low': len([inv for inv in invoices if inv.risk_score < 30]),
                'medium': len([inv for inv in invoices if 30 <= inv.risk_score < 70]),
                'high': len([inv for inv in invoices if inv.risk_score >= 70])
            }
            
            metrics = {
                'total_spend': total_spend,
                'invoice_count': len(invoices),
                'vendor_count': len(vendors),
                'category_count': len(categories),
                'risk_distribution': risk_levels,
                'average_invoice_amount': total_spend / len(invoices) if invoices else 0,
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify(metrics)
            
        except Exception as e:
            app.logger.error(f"Error generating dashboard metrics: {e}")
            return jsonify({"error": str(e)}), 500
