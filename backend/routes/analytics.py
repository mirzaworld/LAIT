from flask import Blueprint, request, jsonify
from sqlalchemy import func, desc, asc, and_, extract, text
from backend.db.database import get_db_session
from backend.models.db_models import Invoice, LineItem, Vendor, Matter, RiskFactor
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.auth import role_required
from datetime import datetime, timedelta
import calendar
from backend.models.vendor_analyzer import VendorAnalyzer
from backend.models.matter_analyzer import MatterAnalyzer

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/summary', methods=['GET'])
@jwt_required
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
@jwt_required
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
@jwt_required
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
@jwt_required
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
@jwt_required
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
@jwt_required
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
@jwt_required
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
@jwt_required
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
@jwt_required
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
@jwt_required
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
