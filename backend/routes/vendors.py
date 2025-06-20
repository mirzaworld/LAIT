from flask import Blueprint, jsonify, request
from sqlalchemy import func, desc, asc, and_, or_, text
from backend.db.database import get_db_session
from backend.models.db_models import Vendor, Invoice, LineItem
from backend.dev_auth import development_jwt_required
from datetime import datetime, timedelta

vendors_bp = Blueprint('vendors', __name__, url_prefix='/api/vendors')

@vendors_bp.route('', methods=['GET'])
@development_jwt_required
def list_vendors():
    """Get all vendors"""
    session = get_db_session()
    try:
        # Check if there are any vendors in the database
        vendor_count = session.query(Vendor).count()
        
        # If no vendors in database, return demo data
        if vendor_count == 0:
            demo_vendors = [
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
            
            return jsonify({'vendors': demo_vendors})
        
        # If there are vendors, try to fetch them safely
        vendors = session.query(Vendor.id, Vendor.name).all()
        vendor_list = []
        for vendor in vendors:
            vendor_list.append({
                'id': vendor.id,
                'name': vendor.name,
                'category': 'Unknown',
                'spend': 0,  # Would need to calculate from invoices
                'matter_count': 0,  # Would need to calculate
                'avg_rate': 0,  # Would need to calculate
                'performance_score': 85,  # Default
                'diversity_score': 75,  # Default
                'on_time_rate': 90  # Default
            })
        
        return jsonify({'vendors': vendor_list})
        
    except Exception as e:
        # Return demo data on any error
        demo_vendors = [
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
            }
        ]
        return jsonify({'vendors': demo_vendors})
    finally:
        session.close()

@vendors_bp.route('/search', methods=['GET'])
@development_jwt_required
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

@vendors_bp.route('/discovery', methods=['GET'])
@development_jwt_required
def vendor_discovery():
    """Discover new potential vendors based on requirements"""
    session = get_db_session()
    try:
        # Get discovery criteria
        practice_areas = request.args.getlist('practice_area')
        locations = request.args.getlist('location')
        
        # Build discovery query - find prospects
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
        
        prospects = query.limit(50).all()
        
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
                    'location': f"{prospect.city}, {prospect.state_province}" if prospect.city else prospect.state_province,
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
                'locations': locations
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error in vendor discovery: {str(e)}'}), 500
    finally:
        session.close()

@vendors_bp.route('/analytics/summary', methods=['GET'])
@development_jwt_required
def vendor_analytics_summary():
    """Get summary analytics for vendor portfolio"""
    session = get_db_session()
    try:
        # Portfolio composition
        total_vendors = session.query(func.count(Vendor.id)).scalar() or 0
        active_vendors = session.query(func.count(Vendor.id))\
            .filter(Vendor.status == 'Active').scalar() or 0
        prospect_vendors = session.query(func.count(Vendor.id))\
            .filter(Vendor.status == 'Prospect').scalar() or 0
        
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
                'practice_areas': [{'area': pa.practice_area or 'Unknown', 'count': pa.count} for pa in practice_areas],
                'geographic': [{'country': gd.country or 'Unknown', 'count': gd.count} for gd in geographic_dist],
                'firm_sizes': [{'size': sd.firm_size_category or 'Unknown', 'count': sd.count} for sd in size_dist]
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating vendor analytics: {str(e)}'}), 500
    finally:
        session.close()

def calculate_prospect_score(vendor):
    """Calculate a discovery score for vendor prospects"""
    score = 50  # Base score
    
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
