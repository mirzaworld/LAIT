"""
Enhanced Vendor Management Routes for LAIT
Incorporates company dataset insights for better vendor analytics and management
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func, desc, asc, and_, or_, text
from db.database import get_db_session
from models.db_models import Vendor, VendorMarketInsight, VendorBenchmark, Invoice, LineItem
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional

vendor_mgmt_bp = Blueprint('vendor_management', __name__)

@vendor_mgmt_bp.route('/search', methods=['GET'])
@jwt_required()
def search_vendors():
    """Advanced vendor search with filters"""
    session = get_db_session()
    try:
        # Get search parameters
        name = request.args.get('name', '')
        practice_area = request.args.get('practice_area')
        firm_size = request.args.get('firm_size')
        location = request.args.get('location')
        country = request.args.get('country')
        min_performance = request.args.get('min_performance_score', type=float)
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Build query
        query = session.query(Vendor)
        
        # Apply filters
        if name:
            query = query.filter(Vendor.name.ilike(f'%{name}%'))
        if practice_area:
            query = query.filter(Vendor.practice_area == practice_area)
        if firm_size:
            query = query.filter(Vendor.firm_size_category == firm_size)
        if location:
            query = query.filter(
                or_(
                    Vendor.city.ilike(f'%{location}%'),
                    Vendor.state_province.ilike(f'%{location}%')
                )
            )
        if country:
            query = query.filter(Vendor.country == country)
        if min_performance:
            query = query.filter(Vendor.performance_score >= min_performance)
        if status:
            query = query.filter(Vendor.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        vendors = query.offset(offset).limit(per_page).all()
        
        # Format results
        results = []
        for vendor in vendors:
            results.append({
                'id': vendor.id,
                'name': vendor.name,
                'practice_area': vendor.practice_area,
                'firm_size_category': vendor.firm_size_category,
                'location': f"{vendor.city}, {vendor.state_province}" if vendor.city else vendor.state_province,
                'country': vendor.country,
                'performance_score': vendor.performance_score,
                'status': vendor.status,
                'total_spend': vendor.total_spend,
                'website': vendor.website
            })
        
        return jsonify({
            'vendors': results,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error searching vendors: {str(e)}'}), 500
    finally:
        session.close()

@vendor_mgmt_bp.route('/market-insights', methods=['GET'])
@jwt_required()
def get_market_insights():
    """Get market insights for vendor landscape analysis"""
    session = get_db_session()
    try:
        practice_area = request.args.get('practice_area')
        region = request.args.get('region')
        
        # Build base query
        query = session.query(VendorMarketInsight)
        
        if practice_area:
            query = query.filter(VendorMarketInsight.practice_area == practice_area)
        if region:
            query = query.filter(VendorMarketInsight.region == region)
            
        insights = query.all()
        
        # If no specific insights found, generate from current vendor data
        if not insights:
            insights = generate_market_insights(session, practice_area, region)
        
        results = []
        for insight in insights:
            results.append({
                'practice_area': insight.practice_area,
                'region': insight.region,
                'country': insight.country,
                'total_firms': insight.total_firms,
                'avg_firm_size': insight.avg_firm_size,
                'market_concentration': insight.market_concentration,
                'top_firms': insight.top_5_firms,
                'emerging_firms_count': insight.emerging_firms_count,
                'major_cities': insight.major_cities,
                'updated_at': insight.updated_at.isoformat() if insight.updated_at else None
            })
        
        return jsonify({'market_insights': results})
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving market insights: {str(e)}'}), 500
    finally:
        session.close()

@vendor_mgmt_bp.route('/<int:vendor_id>/benchmark', methods=['GET'])
@jwt_required()
def get_vendor_benchmark(vendor_id):
    """Get comprehensive benchmarking data for a vendor"""
    session = get_db_session()
    try:
        vendor = session.query(Vendor).get(vendor_id)
        if not vendor:
            return jsonify({'error': 'Vendor not found'}), 404
        
        # Get existing benchmarks
        benchmarks = session.query(VendorBenchmark)\
            .filter(VendorBenchmark.vendor_id == vendor_id)\
            .order_by(desc(VendorBenchmark.created_at))\
            .all()
        
        # Generate fresh benchmarks if none exist or outdated
        if not benchmarks or (datetime.utcnow() - benchmarks[0].created_at).days > 30:
            benchmarks = generate_vendor_benchmarks(session, vendor)
        
        # Format benchmark data
        benchmark_data = {}
        for benchmark in benchmarks:
            benchmark_data[benchmark.benchmark_type] = {
                'vendor_value': benchmark.vendor_value,
                'market_average': benchmark.market_average,
                'market_median': benchmark.market_median,
                'percentile_rank': benchmark.percentile_rank,
                'peer_average': benchmark.peer_average,
                'peer_group': benchmark.peer_group
            }
        
        # Get comparative analytics
        peer_analysis = get_peer_analysis(session, vendor)
        
        return jsonify({
            'vendor': {
                'id': vendor.id,
                'name': vendor.name,
                'practice_area': vendor.practice_area,
                'firm_size_category': vendor.firm_size_category
            },
            'benchmarks': benchmark_data,
            'peer_analysis': peer_analysis
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating vendor benchmark: {str(e)}'}), 500
    finally:
        session.close()

@vendor_mgmt_bp.route('/discovery', methods=['GET'])
@jwt_required()
def vendor_discovery():
    """Discover new potential vendors based on requirements"""
    session = get_db_session()
    try:
        # Get discovery criteria
        practice_areas = request.args.getlist('practice_area')
        max_firm_size = request.args.get('max_firm_size')
        min_firm_size = request.args.get('min_firm_size')
        locations = request.args.getlist('location')
        exclude_current = request.args.get('exclude_current', 'true').lower() == 'true'
        
        # Build discovery query
        query = session.query(Vendor).filter(Vendor.status == 'Prospect')
        
        if practice_areas:
            query = query.filter(Vendor.practice_area.in_(practice_areas))
        
        if locations:
            location_filters = []
            for location in locations:
                location_filters.append(Vendor.city.ilike(f'%{location}%'))
                location_filters.append(Vendor.state_province.ilike(f'%{location}%'))
                location_filters.append(Vendor.country.ilike(f'%{location}%'))
            query = query.filter(or_(*location_filters))
        
        # Size filters
        size_order = ['1-10', '11-50', '51-200', '201-500', '501-1000', '1000+']
        if min_firm_size and min_firm_size in size_order:
            min_index = size_order.index(min_firm_size)
            valid_sizes = size_order[min_index:]
            query = query.filter(Vendor.employee_count.in_(valid_sizes))
        
        if max_firm_size and max_firm_size in size_order:
            max_index = size_order.index(max_firm_size)
            valid_sizes = size_order[:max_index + 1]
            query = query.filter(Vendor.employee_count.in_(valid_sizes))
        
        # Exclude current vendors if requested
        if exclude_current:
            active_vendor_ids = session.query(Vendor.id).filter(Vendor.status == 'Active').subquery()
            query = query.filter(~Vendor.id.in_(active_vendor_ids))
        
        # Order by potential value (combination of factors)
        prospects = query.limit(100).all()
        
        # Score and rank prospects
        scored_prospects = []
        for prospect in prospects:
            score = calculate_prospect_score(prospect)
            scored_prospects.append({
                'vendor': {
                    'id': prospect.id,
                    'name': prospect.name,
                    'practice_area': prospect.practice_area,
                    'firm_size_category': prospect.firm_size_category,
                    'location': f"{prospect.city}, {prospect.state_province}",
                    'country': prospect.country,
                    'website': prospect.website,
                    'founded_year': prospect.founded_year
                },
                'discovery_score': score,
                'reasons': generate_discovery_reasons(prospect, practice_areas, locations)
            })
        
        # Sort by discovery score
        scored_prospects.sort(key=lambda x: x['discovery_score'], reverse=True)
        
        return jsonify({
            'discovered_vendors': scored_prospects[:20],  # Top 20 prospects
            'criteria': {
                'practice_areas': practice_areas,
                'locations': locations,
                'size_range': f"{min_firm_size} - {max_firm_size}" if min_firm_size or max_firm_size else "Any"
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error in vendor discovery: {str(e)}'}), 500
    finally:
        session.close()

@vendor_mgmt_bp.route('/analytics/summary', methods=['GET'])
@jwt_required()
def vendor_analytics_summary():
    """Get summary analytics for vendor portfolio"""
    session = get_db_session()
    try:
        # Portfolio composition
        total_vendors = session.query(func.count(Vendor.id)).scalar()
        active_vendors = session.query(func.count(Vendor.id))\
            .filter(Vendor.status == 'Active').scalar()
        prospect_vendors = session.query(func.count(Vendor.id))\
            .filter(Vendor.status == 'Prospect').scalar()
        
        # Practice area distribution
        practice_areas = session.query(
            Vendor.practice_area,
            func.count(Vendor.id).label('count')
        ).filter(Vendor.status == 'Active')\
         .group_by(Vendor.practice_area)\
         .order_by(desc('count'))\
         .all()
        
        # Geographic distribution
        geographic_dist = session.query(
            Vendor.country,
            func.count(Vendor.id).label('count')
        ).filter(Vendor.status == 'Active')\
         .group_by(Vendor.country)\
         .order_by(desc('count'))\
         .limit(10)\
         .all()
        
        # Firm size distribution
        size_dist = session.query(
            Vendor.firm_size_category,
            func.count(Vendor.id).label('count')
        ).filter(Vendor.status == 'Active')\
         .group_by(Vendor.firm_size_category)\
         .order_by(desc('count'))\
         .all()
        
        # Performance metrics
        avg_performance = session.query(func.avg(Vendor.performance_score))\
            .filter(Vendor.status == 'Active').scalar() or 0
        
        # Spend distribution
        total_spend = session.query(func.sum(Vendor.total_spend))\
            .filter(Vendor.status == 'Active').scalar() or 0
        
        return jsonify({
            'portfolio_summary': {
                'total_vendors': total_vendors,
                'active_vendors': active_vendors,
                'prospect_vendors': prospect_vendors,
                'avg_performance_score': round(avg_performance, 2),
                'total_spend': total_spend
            },
            'distributions': {
                'practice_areas': [{'area': pa.practice_area, 'count': pa.count} for pa in practice_areas],
                'geographic': [{'country': gd.country, 'count': gd.count} for gd in geographic_dist],
                'firm_sizes': [{'size': sd.firm_size_category, 'count': sd.count} for sd in size_dist]
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating vendor analytics: {str(e)}'}), 500
    finally:
        session.close()

# Helper functions

def generate_market_insights(session, practice_area=None, region=None):
    """Generate market insights from current vendor data"""
    # This would analyze the vendor database to create market insights
    # Implementation depends on available data
    return []

def generate_vendor_benchmarks(session, vendor):
    """Generate fresh benchmark data for a vendor"""
    benchmarks = []
    
    # Rate benchmarking
    if vendor.avg_rate:
        market_avg_rate = session.query(func.avg(Vendor.avg_rate))\
            .filter(Vendor.practice_area == vendor.practice_area).scalar()
        
        if market_avg_rate:
            rate_benchmark = VendorBenchmark(
                vendor_id=vendor.id,
                benchmark_type='Average Rate',
                vendor_value=vendor.avg_rate,
                market_average=market_avg_rate,
                percentile_rank=calculate_percentile_rank(session, vendor, 'avg_rate')
            )
            session.add(rate_benchmark)
            benchmarks.append(rate_benchmark)
    
    session.commit()
    return benchmarks

def get_peer_analysis(session, vendor):
    """Get peer comparison analysis"""
    # Find similar vendors
    peers = session.query(Vendor)\
        .filter(Vendor.practice_area == vendor.practice_area)\
        .filter(Vendor.firm_size_category == vendor.firm_size_category)\
        .filter(Vendor.id != vendor.id)\
        .limit(10)\
        .all()
    
    return {
        'peer_count': len(peers),
        'avg_peer_performance': sum(p.performance_score or 0 for p in peers) / len(peers) if peers else 0,
        'peer_names': [p.name for p in peers[:5]]  # Top 5 peer names
    }

def calculate_prospect_score(vendor):
    """Calculate a discovery score for vendor prospects"""
    score = 0
    
    # Base score
    score += 50
    
    # Firm size bonus (medium size firms often good prospects)
    if vendor.firm_size_category in ['Small to Medium Law Firm', 'Mid-Size Law Firm']:
        score += 20
    elif vendor.firm_size_category == 'Large Law Firm':
        score += 15
    
    # Established firm bonus
    if vendor.founded_year and vendor.founded_year < 2000:
        score += 10
    
    # Website presence bonus
    if vendor.website:
        score += 5
    
    return min(score, 100)  # Cap at 100

def generate_discovery_reasons(vendor, target_areas, target_locations):
    """Generate reasons why this vendor was discovered"""
    reasons = []
    
    if vendor.practice_area in target_areas:
        reasons.append(f"Specializes in {vendor.practice_area}")
    
    if any(loc.lower() in (vendor.city or '').lower() or 
           loc.lower() in (vendor.state_province or '').lower() 
           for loc in target_locations):
        reasons.append(f"Located in target region")
    
    if vendor.website:
        reasons.append("Has established web presence")
    
    if vendor.founded_year and vendor.founded_year < 2010:
        reasons.append("Established firm with experience")
    
    return reasons

def calculate_percentile_rank(session, vendor, metric):
    """Calculate percentile rank for a vendor metric"""
    # Simplified percentile calculation
    if not hasattr(vendor, metric):
        return 50
    
    vendor_value = getattr(vendor, metric)
    if not vendor_value:
        return 50
    
    # Count vendors with lower values in same practice area
    lower_count = session.query(func.count(Vendor.id))\
        .filter(Vendor.practice_area == vendor.practice_area)\
        .filter(getattr(Vendor, metric) < vendor_value)\
        .scalar()
    
    total_count = session.query(func.count(Vendor.id))\
        .filter(Vendor.practice_area == vendor.practice_area)\
        .filter(getattr(Vendor, metric).isnot(None))\
        .scalar()
    
    if total_count == 0:
        return 50
    
    return (lower_count / total_count) * 100
