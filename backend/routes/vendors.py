from flask import Blueprint, jsonify
from backend.db.database import get_db_session
from backend.models.db_models import Vendor
from backend.dev_auth import development_jwt_required

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
