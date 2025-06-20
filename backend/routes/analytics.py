from flask import Blueprint, request, jsonify
from sqlalchemy import func, desc, asc, and_, extract, text
from backend.db.database import get_db_session
from backend.models.db_models import Invoice, LineItem, Vendor, Matter, RiskFactor
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.auth import role_required
from backend.dev_auth import development_jwt_required
from datetime import datetime, timedelta
import calendar
from backend.models.vendor_analyzer import VendorAnalyzer
from backend.models.matter_analyzer import MatterAnalyzer
from backend.models.enhanced_invoice_analyzer import analyze_invoice_enhanced

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/summary', methods=['GET'])
@development_jwt_required
def summary():
    """Get summary analytics for dashboard"""
    session = get_db_session()
    try:
        # Get date range parameters
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Default to last 12 months if not specified
        if not date_from:
            date_from = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
            
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        
        # Calculate key metrics
        total_spend = session.query(func.sum(Invoice.amount))\
            .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj)\
            .scalar() or 0
            
        invoice_count = session.query(func.count(Invoice.id))\
            .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj)\
            .scalar() or 0
            
        # Calculate previous period for comparison
        date_diff = date_to_obj - date_from_obj
        prev_date_from = date_from_obj - date_diff
        prev_date_to = date_to_obj - date_diff
        
        prev_total_spend = session.query(func.sum(Invoice.amount))\
            .filter(Invoice.date >= prev_date_from, Invoice.date <= prev_date_to)\
            .scalar() or 0
            
        # Calculate change percentage
        if prev_total_spend > 0:
            spend_change_pct = ((total_spend - prev_total_spend) / prev_total_spend) * 100
        else:
            spend_change_pct = 0
            
        # Calculate active matters
        active_matters_count = session.query(func.count(Matter.id))\
            .join(Invoice, Matter.id == Invoice.matter_id)\
            .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj)\
            .group_by(Matter.id)\
            .count() or 0
            
        # Calculate risk metrics
        risk_factors_count = session.query(func.count(RiskFactor.id))\
            .join(Invoice, RiskFactor.invoice_id == Invoice.id)\
            .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj)\
            .scalar() or 0
            
        high_risk_invoices_count = session.query(func.count(Invoice.id))\
            .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj, Invoice.risk_score >= 7)\
            .scalar() or 0
            
        # Calculate average processing time in days
        # This assumes we track when an invoice was created and when its status changed to 'approved'
        # For now we'll just return a dummy value
        avg_processing_time = 4.5  # days
        
        # Get monthly spend data for charts
        monthly_spend = []
        current_date = date_from_obj.replace(day=1)
        
        while current_date <= date_to_obj:
            # Find the last day of the current month
            _, last_day = calendar.monthrange(current_date.year, current_date.month)
            end_of_month = current_date.replace(day=last_day)
            
            if end_of_month > date_to_obj:
                end_of_month = date_to_obj
                
            month_spend = session.query(func.sum(Invoice.amount))\
                .filter(Invoice.date >= current_date, Invoice.date <= end_of_month)\
                .scalar() or 0
                
            monthly_spend.append({
                'period': current_date.strftime('%Y-%m'),
                'amount': month_spend
            })
            
            # Move to first day of next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year+1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month+1)
                
        # If no data exists, return some demo data for testing
        if total_spend == 0 and invoice_count == 0:
            total_spend = 2847392  # Demo data
            spend_change_pct = 12.5
            invoice_count = 156
            active_matters_count = 47
            risk_factors_count = 23
            high_risk_invoices_count = 8
            avg_processing_time = 3.2
            
            # Create demo monthly data
            monthly_spend = []
            demo_amounts = [245000, 189000, 298000, 167000, 223000, 334000, 278000, 192000, 265000, 301000, 256000, 312000]
            months = ['2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12', '2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06']
            
            for i, month in enumerate(months):
                monthly_spend.append({
                    'period': month,
                    'amount': demo_amounts[i]
                })
                
        return jsonify({
            'total_spend': total_spend,
            'spend_change_percentage': spend_change_pct,
            'invoice_count': invoice_count,
            'active_matters': active_matters_count,
            'risk_factors_count': risk_factors_count,
            'high_risk_invoices_count': high_risk_invoices_count,
            'avg_processing_time': avg_processing_time,
            'date_range': {
                'from': date_from,
                'to': date_to
            },
            'trend_data': {
                'monthly_spend': monthly_spend
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating analytics: {str(e)}'}), 500
    finally:
        session.close()

@analytics_bp.route('/vendors', methods=['GET'])
@development_jwt_required
def vendors():
    """Get vendor comparison analytics"""
    session = get_db_session()
    try:
        # Get date range parameters
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Default to last 12 months if not specified
        if not date_from:
            date_from = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
            
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        
        # Get vendor performance data
        vendor_data = session.query(
            Vendor.id,
            Vendor.name,
            func.sum(Invoice.amount).label('total_spend'),
            func.count(Invoice.id).label('invoice_count'),
            func.avg(Invoice.risk_score).label('avg_risk_score'),
            func.avg(LineItem.rate).label('avg_rate')
        ).join(Invoice, Invoice.vendor_id == Vendor.id)\
         .outerjoin(LineItem, LineItem.invoice_id == Invoice.id)\
         .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj)\
         .group_by(Vendor.id, Vendor.name)\
         .order_by(func.sum(Invoice.amount).desc())\
         .all()
         
        vendors = []
        for v in vendor_data:
            # Calculate efficiency score (placeholder)
            efficiency_score = 100 - (10 * (v.avg_risk_score or 0))
            if efficiency_score < 0:
                efficiency_score = 0
                
            vendors.append({
                'id': v.id,
                'name': v.name,
                'total_spend': v.total_spend or 0,
                'invoice_count': v.invoice_count or 0,
                'avg_risk_score': v.avg_risk_score or 0,
                'avg_hourly_rate': v.avg_rate or 0,
                'efficiency_score': efficiency_score,
                'diversity_score': v.diversity_score if hasattr(v, 'diversity_score') else None
            })
            
        # If no vendor data, provide demo data
        if not vendors:
            vendors = [
                {
                    'id': 'V001',
                    'name': 'Morrison & Foerster LLP',
                    'category': 'AmLaw 100',
                    'spend': 734000,
                    'matter_count': 15,
                    'avg_rate': 950,
                    'performance_score': 92,
                    'diversity_score': 78,
                    'on_time_rate': 94
                },
                {
                    'id': 'V002',
                    'name': 'Baker McKenzie',
                    'category': 'Global',
                    'spend': 589000,
                    'matter_count': 18,
                    'avg_rate': 850,
                    'performance_score': 88,
                    'diversity_score': 82,
                    'on_time_rate': 97
                },
                {
                    'id': 'V003',
                    'name': 'Latham & Watkins',
                    'category': 'AmLaw 100',
                    'spend': 623000,
                    'matter_count': 12,
                    'avg_rate': 1100,
                    'performance_score': 90,
                    'diversity_score': 68,
                    'on_time_rate': 96
                },
                {
                    'id': 'V004',
                    'name': 'Skadden Arps',
                    'category': 'AmLaw 100',
                    'spend': 435000,
                    'matter_count': 7,
                    'avg_rate': 1050,
                    'performance_score': 88,
                    'diversity_score': 65,
                    'on_time_rate': 92
                },
                {
                    'id': 'V005',
                    'name': 'White & Case',
                    'category': 'Global',
                    'spend': 312000,
                    'matter_count': 9,
                    'avg_rate': 900,
                    'performance_score': 82,
                    'diversity_score': 75,
                    'on_time_rate': 90
                }
            ]
            
        # Calculate global average metrics
        global_avg_rate = session.query(func.avg(LineItem.rate))\
            .join(Invoice, LineItem.invoice_id == Invoice.id)\
            .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj)\
            .scalar() or 0
            
        global_avg_risk = session.query(func.avg(Invoice.risk_score))\
            .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj)\
            .scalar() or 0
            
        return jsonify({
            'vendors': vendors,
            'benchmarks': {
                'avg_hourly_rate': global_avg_rate,
                'avg_risk_score': global_avg_risk
            },
            'date_range': {
                'from': date_from,
                'to': date_to
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating vendor analytics: {str(e)}'}), 500
    finally:
        session.close()

@analytics_bp.route('/forecast', methods=['GET'])
@jwt_required()
def forecast():
    """Get forecasted spend data"""
    session = get_db_session()
    try:
        # Get number of months to forecast
        months = int(request.args.get('months', 6))
        
        # Get historical data for the last 12 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Get monthly historical data
        historical_data = []
        current_date = start_date.replace(day=1)
        
        while current_date < end_date:
            # Find the last day of the current month
            _, last_day = calendar.monthrange(current_date.year, current_date.month)
            end_of_month = current_date.replace(day=last_day)
            
            if end_of_month > end_date:
                end_of_month = end_date
                
            month_spend = session.query(func.sum(Invoice.amount))\
                .filter(Invoice.date >= current_date, Invoice.date <= end_of_month)\
                .scalar() or 0
                
            historical_data.append({
                'period': current_date.strftime('%Y-%m'),
                'amount': month_spend
            })
            
            # Move to first day of next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year+1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month+1)
        
        # Generate forecast data
        # In a real implementation, this would use ML models
        # Here we'll just use a simple moving average
        forecast_data = []
        
        # Calculate the average monthly spend from historical data
        total_spend = sum(item['amount'] for item in historical_data)
        avg_monthly_spend = total_spend / len(historical_data) if historical_data else 0
        
        # Create forecast for the requested number of months
        for i in range(months):
            # In a simplistic model, increase by 2% each month
            forecast_amount = avg_monthly_spend * (1 + (i * 0.02))
            
            # Calculate the forecast period
            forecast_date = end_date + timedelta(days=30 * (i + 1))
            forecast_period = forecast_date.strftime('%Y-%m')
            
            forecast_data.append({
                'period': forecast_period,
                'amount': forecast_amount,
                'low_estimate': forecast_amount * 0.8,
                'high_estimate': forecast_amount * 1.2
            })
            
        return jsonify({
            'historical_data': historical_data,
            'forecast_data': forecast_data,
            'forecast_months': months
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating spend forecast: {str(e)}'}), 500
    finally:
        session.close()

@analytics_bp.route('/risk-factors', methods=['GET'])
@jwt_required()
def get_risk_factor_analysis():
    """Get analysis of risk factors"""
    session = get_db_session()
    try:
        # Get date range parameters
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Default to last 12 months if not specified
        if not date_from:
            date_from = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
            
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        
        # Get risk factors by type
        risk_factors_by_type = session.query(
            RiskFactor.factor_type,
            func.count(RiskFactor.id).label('count'),
            func.avg(RiskFactor.impact_score).label('avg_impact')
        ).join(Invoice, RiskFactor.invoice_id == Invoice.id)\
         .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj)\
         .group_by(RiskFactor.factor_type)\
         .order_by(func.count(RiskFactor.id).desc())\
         .all()
         
        risk_types = []
        for rf in risk_factors_by_type:
            risk_types.append({
                'type': rf.factor_type,
                'count': rf.count,
                'avg_impact': rf.avg_impact or 0
            })
            
        # Get risk factors by severity
        risk_factors_by_severity = session.query(
            RiskFactor.severity,
            func.count(RiskFactor.id).label('count')
        ).join(Invoice, RiskFactor.invoice_id == Invoice.id)\
         .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj)\
         .group_by(RiskFactor.severity)\
         .order_by(func.count(RiskFactor.id).desc())\
         .all()
         
        risk_severity = []
        for rs in risk_factors_by_severity:
            risk_severity.append({
                'severity': rs.severity,
                'count': rs.count
            })
            
        # Get risk factors by vendor
        risk_factors_by_vendor = session.query(
            Vendor.id,
            Vendor.name,
            func.count(RiskFactor.id).label('count')
        ).join(Invoice, RiskFactor.invoice_id == Invoice.id)\
         .join(Vendor, Invoice.vendor_id == Vendor.id)\
         .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj)\
         .group_by(Vendor.id, Vendor.name)\
         .order_by(func.count(RiskFactor.id).desc())\
         .limit(10)\
         .all()
         
        vendor_risks = []
        for vr in risk_factors_by_vendor:
            vendor_risks.append({
                'vendor_id': vr.id,
                'vendor_name': vr.name,
                'risk_count': vr.count
            })
            
        return jsonify({
            'risk_by_type': risk_types,
            'risk_by_severity': risk_severity,
            'risk_by_vendor': vendor_risks,
            'date_range': {
                'from': date_from,
                'to': date_to
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating risk analysis: {str(e)}'}), 500
    finally:
        session.close()

@analytics_bp.route('/vendor/<vendor_id>/risk_profile', methods=['GET'])
@jwt_required()
def vendor_risk_profile(vendor_id):
    """Get advanced risk profile and analytics for a specific vendor."""
    current_user = get_jwt_identity()
    try:
        analyzer = VendorAnalyzer()
        profile = analyzer.advanced_risk_profile(vendor_id)
        return jsonify(profile)
    except Exception as e:
        return jsonify({'error': f'Error generating vendor risk profile: {str(e)}'}), 500

@analytics_bp.route('/matters', methods=['GET'])
@jwt_required()
def matter_analytics_list():
    """Get matter comparison analytics"""
    current_user = get_jwt_identity()
    session = get_db_session()
    try:
        # Get date range parameters
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Default to last 12 months if not specified
        if not date_from:
            date_from = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
            
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        
        # Get matter performance data
        matter_data = session.query(
            Matter.id,
            Matter.name,
            func.sum(Invoice.amount).label('total_spend'),
            func.count(Invoice.id).label('invoice_count'),
            func.avg(Invoice.risk_score).label('avg_risk_score'),
            func.avg(LineItem.rate).label('avg_rate')
        ).join(Invoice, Invoice.matter_id == Matter.id)\
         .outerjoin(LineItem, LineItem.invoice_id == Invoice.id)\
         .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj)\
         .group_by(Matter.id, Matter.name)\
         .order_by(func.sum(Invoice.amount).desc())\
         .all()
         
        matters = []
        for m in matter_data:
            # Calculate efficiency score (placeholder)
            efficiency_score = 100 - (10 * (m.avg_risk_score or 0))
            if efficiency_score < 0:
                efficiency_score = 0
                
            matters.append({
                'id': m.id,
                'name': m.name,
                'total_spend': m.total_spend or 0,
                'invoice_count': m.invoice_count or 0,
                'avg_risk_score': m.avg_risk_score or 0,
                'avg_hourly_rate': m.avg_rate or 0,
                'efficiency_score': efficiency_score
            })
            
        # Calculate global average metrics
        global_avg_rate = session.query(func.avg(LineItem.rate))\
            .join(Invoice, LineItem.invoice_id == Invoice.id)\
            .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj)\
            .scalar() or 0
            
        global_avg_risk = session.query(func.avg(Invoice.risk_score))\
            .filter(Invoice.date >= date_from_obj, Invoice.date <= date_to_obj)\
            .scalar() or 0
            
        return jsonify({
            'matters': matters,
            'benchmarks': {
                'avg_hourly_rate': global_avg_rate,
                'avg_risk_score': global_avg_risk
            },
            'date_range': {
                'from': date_from,
                'to': date_to
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating matter analytics: {str(e)}'}), 500
    finally:
        session.close()

@analytics_bp.route('/matter/<matter_id>/risk_profile', methods=['GET'])
@jwt_required()
def matter_risk_profile(matter_id):
    """Get advanced risk profile and analytics for a specific matter."""
    current_user = get_jwt_identity()
    try:
        analyzer = MatterAnalyzer()
        profile = analyzer.analyze_matter_risk(matter_id)
        return jsonify(profile)
    except Exception as e:
        return jsonify({'error': f'Error generating matter risk profile: {str(e)}'}), 500

@analytics_bp.route('/matter/<matter_id>/forecast', methods=['GET'])
@jwt_required()
def matter_expense_forecast(matter_id):
    """Get expense forecast for a specific matter."""
    current_user = get_jwt_identity()
    try:
        analyzer = MatterAnalyzer()
        forecast = analyzer.forecast_expenses(matter_id)
        return jsonify(forecast)
    except Exception as e:
        return jsonify({'error': f'Error generating matter expense forecast: {str(e)}'}), 500

@analytics_bp.route('/vendor-analytics', methods=['GET'])
@jwt_required()
def vendor_analytics():
    """Get analytics for top vendors"""
    current_user = get_jwt_identity()
    session = get_db_session()
    try:
        # Fetch top vendors by spend
        top_vendors = session.query(Vendor.name, func.sum(Invoice.amount).label('total_spend'))\
            .join(Invoice, Vendor.id == Invoice.vendor_id)\
            .group_by(Vendor.name)\
            .order_by(desc('total_spend'))\
            .limit(10).all()

        result = [{'vendor_name': v[0], 'total_spend': v[1]} for v in top_vendors]
        return jsonify(result)
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@analytics_bp.route('/spend-forecast', methods=['GET'])
@jwt_required()
def general_spend_forecast():
    """Get spend forecast for the next period"""
    current_user = get_jwt_identity()
    session = get_db_session()
    try:
        # Fetch historical spend data
        historical_data = session.query(Invoice.date, func.sum(Invoice.amount).label('total_spend'))\
            .group_by(Invoice.date)\
            .order_by(Invoice.date).all()

        # Use forecasting model (mocked for now)
        forecast_model = MatterAnalyzer()
        forecast = forecast_model.forecast_spend(historical_data)

        return jsonify({'forecast': forecast})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@analytics_bp.route('/enhanced-analysis', methods=['POST'])
@jwt_required()
def enhanced_analysis():
    """Get enhanced ML analysis using real-world legal billing data"""
    try:
        # Get invoice data from request
        invoice_data = request.get_json()
        
        if not invoice_data:
            return jsonify({'error': 'No invoice data provided'}), 400
        
        # Perform enhanced analysis
        analysis_result = analyze_invoice_enhanced(invoice_data)
        
        return jsonify({
            'status': 'success',
            'analysis': analysis_result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Enhanced analysis failed: {str(e)}'
        }), 500

@analytics_bp.route('/ml-models/status', methods=['GET'])
@jwt_required()
def ml_models_status():
    """Get status of ML models"""
    try:
        import os
        models_dir = '/app/backend/ml/models'
        
        # Check what model files exist
        model_files = []
        if os.path.exists(models_dir):
            model_files = [f for f in os.listdir(models_dir) if f.endswith('.joblib')]
        
        # Check for benchmark file
        benchmark_file = os.path.join(models_dir, 'rate_benchmarks.json')
        has_benchmarks = os.path.exists(benchmark_file)
        
        models_status = {
            'models_directory': models_dir,
            'model_files': model_files,
            'has_benchmarks': has_benchmarks,
            'total_files': len(model_files)
        }
        
        return jsonify({
            'status': 'success',
            'models': models_status
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Failed to check model status: {str(e)}'
        }), 500

@analytics_bp.route('/spend-trends', methods=['GET'])
@development_jwt_required
def spend_trends():
    """Get spend trends data for charts"""
    session = get_db_session()
    try:
        # Get parameters
        period = request.args.get('period', 'monthly')
        category = request.args.get('category')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Default to last 12 months if not specified
        if not date_from:
            date_from = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
            
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        
        # Build base query
        query = session.query(Invoice).filter(
            Invoice.date >= date_from_obj,
            Invoice.date <= date_to_obj
        )
        
        # Filter by category if provided
        if category and category != 'all':
            query = query.join(Matter).filter(Matter.category == category)
        
        labels = []
        datasets = []
        
        if period == 'monthly':
            # Group by month
            current_date = date_from_obj.replace(day=1)
            monthly_data = {}
            
            while current_date <= date_to_obj:
                # Find the last day of the current month
                _, last_day = calendar.monthrange(current_date.year, current_date.month)
                end_of_month = current_date.replace(day=last_day)
                
                if end_of_month > date_to_obj:
                    end_of_month = date_to_obj
                
                label = current_date.strftime('%b %Y')
                labels.append(label)
                
                # Get spend for this month
                month_spend = session.query(func.sum(Invoice.amount)).filter(
                    Invoice.date >= current_date,
                    Invoice.date <= end_of_month
                ).scalar() or 0
                
                monthly_data[label] = month_spend
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year+1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month+1)
            
            # Create dataset
            datasets.append({
                'label': 'Total Spend',
                'data': [monthly_data[label] for label in labels]
            })
            
            # If no category filter, add breakdown by practice area
            if not category:
                practice_areas = ['Corporate', 'Litigation', 'IP', 'Regulatory', 'Employment']
                colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
                
                for i, area in enumerate(practice_areas):
                    area_data = {}
                    current_date = date_from_obj.replace(day=1)
                    
                    while current_date <= date_to_obj:
                        _, last_day = calendar.monthrange(current_date.year, current_date.month)
                        end_of_month = current_date.replace(day=last_day)
                        
                        if end_of_month > date_to_obj:
                            end_of_month = date_to_obj
                        
                        label = current_date.strftime('%b %Y')
                        
                        # Get spend for this practice area and month
                        area_spend = session.query(func.sum(Invoice.amount)).join(Matter).filter(
                            Invoice.date >= current_date,
                            Invoice.date <= end_of_month,
                            Matter.category == area
                        ).scalar() or 0
                        
                        area_data[label] = area_spend
                        
                        # Move to next month
                        if current_date.month == 12:
                            current_date = current_date.replace(year=current_date.year+1, month=1)
                        else:
                            current_date = current_date.replace(month=current_date.month+1)
                    
                    datasets.append({
                        'label': area,
                        'data': [area_data[label] for label in labels]
                    })
        
        # If no real data, return demo data for testing
        if not any(dataset['data'] for dataset in datasets if any(dataset['data'])):
            # Demo data for chart testing
            labels = ['Jun 2024', 'Jul 2024', 'Aug 2024', 'Sep 2024', 'Oct 2024', 'Nov 2024', 
                     'Dec 2024', 'Jan 2025', 'Feb 2025', 'Mar 2025', 'Apr 2025', 'May 2025', 'Jun 2025']
            
            datasets = [
                {
                    'label': 'Total Spend',
                    'data': [245000, 189000, 298000, 167000, 223000, 334000, 278000, 192000, 265000, 301000, 256000, 312000, 289000]
                },
                {
                    'label': 'Corporate',
                    'data': [98000, 75600, 119200, 66800, 89200, 133600, 111200, 76800, 106000, 120400, 102400, 124800, 115600]
                },
                {
                    'label': 'Litigation', 
                    'data': [73500, 56700, 89400, 50100, 66900, 100200, 83400, 57600, 79500, 90300, 76800, 93600, 86700]
                },
                {
                    'label': 'IP',
                    'data': [49000, 37800, 59600, 33400, 44600, 66800, 55600, 38400, 53000, 60200, 51200, 62400, 57800]
                },
                {
                    'label': 'Regulatory',
                    'data': [24500, 18900, 29800, 16700, 22300, 33400, 27800, 19200, 26500, 30100, 25600, 31200, 28900]
                }
            ]
            
        return jsonify({
            'labels': labels,
            'datasets': datasets
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating spend trends: {str(e)}'}), 500
    finally:
        session.close()
