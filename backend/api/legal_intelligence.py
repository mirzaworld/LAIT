"""
Legal Intelligence API Routes

Provides endpoints for legal research, vendor risk analysis, and legal analytics
integrated with external legal data sources like CourtListener.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import requests
import logging

from ..db.database import get_db_session
from ..models.db_models import User, Vendor, Matter, Invoice

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

legal_intelligence_bp = Blueprint('legal_intelligence', __name__)

# CourtListener API Configuration
COURTLISTENER_API_BASE = 'https://www.courtlistener.com/api/rest/v4'

def get_user_from_token():
    """Get current user from JWT token"""
    current_user_id = get_jwt_identity()
    if not current_user_id:
        return None
    
    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == current_user_id).first()
        return user
    finally:
        db.close()

@legal_intelligence_bp.route('/verify-attorney', methods=['POST'])
@jwt_required()
def verify_attorney():
    """Verify attorney credentials using legal databases"""
    try:
        data = request.get_json()
        attorney_name = data.get('attorney_name')
        bar_number = data.get('bar_number')
        state = data.get('state')
        
        if not attorney_name:
            return jsonify({'error': 'Attorney name is required'}), 400
        
        # Search for attorney in CourtListener judge database
        search_url = f"{COURTLISTENER_API_BASE}/search/"
        params = {
            'type': 'p',  # People (judges/attorneys)
            'q': attorney_name,
            'format': 'json'
        }
        
        response = requests.get(search_url, params=params)
        
        if response.status_code == 200:
            search_results = response.json()
            
            # Process results to find matches
            matches = []
            for result in search_results.get('results', []):
                matches.append({
                    'name': result.get('name_full', ''),
                    'positions': result.get('positions', []),
                    'educations': result.get('educations', []),
                    'political_affiliations': result.get('political_affiliations', [])
                })
            
            return jsonify({
                'verified': len(matches) > 0,
                'matches_found': len(matches),
                'attorney_info': matches[:5],  # Return top 5 matches
                'search_query': attorney_name
            })
        else:
            return jsonify({'error': 'Legal database search failed'}), 500
            
    except Exception as e:
        logger.error(f"Attorney verification error: {str(e)}")
        return jsonify({'error': 'Verification service temporarily unavailable'}), 500

@legal_intelligence_bp.route('/research-case', methods=['POST'])
@jwt_required()
def research_case():
    """Research similar cases and legal precedents"""
    try:
        data = request.get_json()
        case_description = data.get('case_description')
        jurisdiction = data.get('jurisdiction')
        case_type = data.get('case_type')
        
        if not case_description:
            return jsonify({'error': 'Case description is required'}), 400
        
        # Build search query
        search_query = case_description
        
        # Search CourtListener opinions
        search_url = f"{COURTLISTENER_API_BASE}/search/"
        params = {
            'type': 'o',  # Opinions
            'q': search_query,
            'format': 'json',
            'order_by': '-date_filed'
        }
        
        # Add jurisdiction filter if specified
        if jurisdiction and jurisdiction != 'all':
            if jurisdiction == 'federal':
                params['court'] = 'scotus,ca1,ca2,ca3,ca4,ca5,ca6,ca7,ca8,ca9,ca10,ca11,cadc,cafc'
            elif jurisdiction == 'state':
                # Would need to map state courts - simplified for demo
                pass
        
        response = requests.get(search_url, params=params)
        
        if response.status_code == 200:
            search_results = response.json()
            
            # Process and enrich results
            cases = []
            for result in search_results.get('results', [])[:10]:  # Top 10 results
                cases.append({
                    'id': result.get('id'),
                    'case_name': result.get('caseName', ''),
                    'court': result.get('court', ''),
                    'date_filed': result.get('dateFiled', ''),
                    'citation': result.get('citation', []),
                    'snippet': result.get('snippet', ''),
                    'url': result.get('absolute_url', ''),
                    'status': result.get('status', '')
                })
            
            # Calculate relevance score (simplified)
            relevance_score = min(100, len(cases) * 10)
            
            return jsonify({
                'cases_found': len(cases),
                'relevance_score': relevance_score,
                'similar_cases': cases,
                'search_suggestions': generate_search_suggestions(case_description),
                'total_available': search_results.get('count', 0)
            })
        else:
            return jsonify({'error': 'Case research failed'}), 500
            
    except Exception as e:
        logger.error(f"Case research error: {str(e)}")
        return jsonify({'error': 'Research service temporarily unavailable'}), 500

@legal_intelligence_bp.route('/search-precedents', methods=['POST'])
@jwt_required()
def search_precedents():
    """Search for legal precedents and highly cited cases"""
    try:
        data = request.get_json()
        legal_issue = data.get('legal_issue')
        keywords = data.get('keywords', '').split(',') if data.get('keywords') else []
        time_range = data.get('time_range', 'all')
        
        if not legal_issue:
            return jsonify({'error': 'Legal issue description is required'}), 400
        
        # Build comprehensive search query
        search_terms = [legal_issue] + [k.strip() for k in keywords if k.strip()]
        search_query = ' '.join(search_terms)
        
        # Search for precedential opinions
        search_url = f"{COURTLISTENER_API_BASE}/search/"
        params = {
            'type': 'o',
            'q': search_query,
            'stat_Precedential': 'on',  # Only precedential cases
            'order_by': '-citeCount',  # Order by citation count
            'format': 'json'
        }
        
        # Add time range filter
        if time_range != 'all':
            end_date = datetime.now()
            if time_range == 'recent':
                start_date = end_date - timedelta(days=365 * 5)  # Last 5 years
            elif time_range == 'decade':
                start_date = end_date - timedelta(days=365 * 10)  # Last 10 years
            elif time_range == 'quarter_century':
                start_date = end_date - timedelta(days=365 * 25)  # Last 25 years
            else:
                start_date = None
            
            if start_date:
                params['filed_after'] = start_date.strftime('%Y-%m-%d')
        
        response = requests.get(search_url, params=params)
        
        if response.status_code == 200:
            search_results = response.json()
            
            # Process precedents
            precedents = []
            for result in search_results.get('results', [])[:15]:  # Top 15 results
                precedents.append({
                    'id': result.get('id'),
                    'case_name': result.get('caseName', ''),
                    'court': result.get('court', ''),
                    'date_filed': result.get('dateFiled', ''),
                    'citation': result.get('citation', []),
                    'citation_count': result.get('citeCount', 0),
                    'snippet': result.get('snippet', ''),
                    'url': result.get('absolute_url', ''),
                    'precedential_value': calculate_precedential_value(result)
                })
            
            # Sort by precedential value
            precedents.sort(key=lambda x: x['precedential_value'], reverse=True)
            
            return jsonify({
                'precedents_found': len(precedents),
                'precedential_cases': precedents,
                'search_query': search_query,
                'time_range': time_range,
                'total_available': search_results.get('count', 0)
            })
        else:
            return jsonify({'error': 'Precedent search failed'}), 500
            
    except Exception as e:
        logger.error(f"Precedent search error: {str(e)}")
        return jsonify({'error': 'Precedent search service temporarily unavailable'}), 500

@legal_intelligence_bp.route('/analyze-vendor-risk', methods=['POST'])
@jwt_required()
def analyze_vendor_risk():
    """Analyze legal risk for a vendor using legal databases"""
    try:
        data = request.get_json()
        vendor_name = data.get('vendor_name')
        
        if not vendor_name:
            return jsonify({'error': 'Vendor name is required'}), 400
        
        # Check if vendor exists in our database
        db = get_db_session()
        try:
            vendor = db.query(Vendor).filter(Vendor.name.ilike(f'%{vendor_name}%')).first()
        finally:
            db.close()
        
        # Search for litigation involving the vendor
        search_url = f"{COURTLISTENER_API_BASE}/search/"
        
        # Search opinions mentioning the vendor
        opinion_params = {
            'type': 'o',
            'q': f'"{vendor_name}"',
            'format': 'json',
            'order_by': '-date_filed'
        }
        
        # Search PACER data for federal cases
        recap_params = {
            'type': 'r',
            'q': f'"{vendor_name}"',
            'format': 'json',
            'order_by': '-date_filed'
        }
        
        # Execute searches
        opinion_response = requests.get(search_url, params=opinion_params)
        recap_response = requests.get(search_url, params=recap_params)
        
        litigation_cases = []
        regulatory_actions = []
        
        if opinion_response.status_code == 200:
            opinion_results = opinion_response.json()
            for result in opinion_results.get('results', [])[:10]:
                litigation_cases.append({
                    'case_name': result.get('caseName', ''),
                    'court': result.get('court', ''),
                    'date': result.get('dateFiled', ''),
                    'snippet': result.get('snippet', ''),
                    'type': 'Opinion'
                })
        
        if recap_response.status_code == 200:
            recap_results = recap_response.json()
            for result in recap_results.get('results', [])[:10]:
                litigation_cases.append({
                    'case_name': result.get('caseName', ''),
                    'court': result.get('court', ''),
                    'date': result.get('dateFiled', ''),
                    'snippet': result.get('snippet', ''),
                    'type': 'Federal Case'
                })
        
        # Calculate risk score
        risk_score = calculate_vendor_risk_score(
            len(litigation_cases),
            recap_results.get('count', 0) if recap_response.status_code == 200 else 0,
            vendor
        )
        
        return jsonify({
            'vendor_name': vendor_name,
            'risk_score': risk_score,
            'litigation_count': len(litigation_cases),
            'active_federal_cases': recap_results.get('count', 0) if recap_response.status_code == 200 else 0,
            'recent_cases': litigation_cases[:5],
            'risk_factors': identify_risk_factors(litigation_cases),
            'recommendation': get_risk_recommendation(risk_score)
        })
        
    except Exception as e:
        logger.error(f"Vendor risk analysis error: {str(e)}")
        return jsonify({'error': 'Risk analysis service temporarily unavailable'}), 500

@legal_intelligence_bp.route('/court-analytics', methods=['POST'])
@jwt_required()
def court_analytics():
    """Generate analytics for specific courts and practice areas"""
    try:
        data = request.get_json()
        court_id = data.get('court')
        practice_area = data.get('practice_area')
        
        # Get court information
        if court_id:
            court_url = f"{COURTLISTENER_API_BASE}/courts/{court_id}/"
            court_response = requests.get(court_url)
            court_info = court_response.json() if court_response.status_code == 200 else {}
        else:
            court_info = {}
        
        # Get case statistics
        search_params = {
            'type': 'o',
            'format': 'json',
            'filed_after': (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        }
        
        if court_id:
            search_params['court'] = court_id
        if practice_area:
            search_params['q'] = practice_area
        
        search_url = f"{COURTLISTENER_API_BASE}/search/"
        response = requests.get(search_url, params=search_params)
        
        if response.status_code == 200:
            results = response.json()
            
            # Process case data for analytics
            case_trends = analyze_case_trends(results.get('results', []))
            
            return jsonify({
                'court_info': court_info,
                'total_cases_last_year': results.get('count', 0),
                'case_trends': case_trends,
                'average_case_duration': calculate_avg_duration(results.get('results', [])),
                'practice_area': practice_area,
                'generated_at': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Court analytics generation failed'}), 500
            
    except Exception as e:
        logger.error(f"Court analytics error: {str(e)}")
        return jsonify({'error': 'Analytics service temporarily unavailable'}), 500

# Helper functions

def generate_search_suggestions(case_description):
    """Generate search suggestions based on case description"""
    # Simple keyword extraction and suggestion generation
    common_legal_terms = ['contract', 'liability', 'negligence', 'breach', 'damages', 'statute']
    suggestions = []
    
    for term in common_legal_terms:
        if term.lower() in case_description.lower():
            suggestions.append(f"Cases involving {term}")
    
    return suggestions[:3]

def calculate_precedential_value(case_result):
    """Calculate precedential value based on court, citations, and date"""
    court = case_result.get('court', '')
    cite_count = case_result.get('citeCount', 0)
    date_filed = case_result.get('dateFiled', '')
    
    # Base score
    score = 50
    
    # Court hierarchy bonus
    if 'scotus' in court.lower():
        score += 40
    elif 'circuit' in court.lower() or 'ca' in court.lower():
        score += 25
    elif 'district' in court.lower():
        score += 10
    
    # Citation count bonus
    score += min(cite_count * 2, 30)
    
    # Recency penalty (older cases may be less relevant)
    try:
        if date_filed:
            case_year = int(date_filed[:4])
            current_year = datetime.now().year
            age_penalty = max(0, (current_year - case_year) * 0.5)
            score -= age_penalty
    except:
        pass
    
    return max(0, min(100, score))

def calculate_vendor_risk_score(litigation_count, federal_cases, vendor=None):
    """Calculate vendor risk score based on litigation history"""
    base_score = 20  # Everyone starts with some base risk
    
    # Litigation count factor
    litigation_factor = min(litigation_count * 15, 60)
    
    # Federal case factor (more serious)
    federal_factor = min(federal_cases * 10, 40)
    
    # Vendor size factor (if available)
    size_factor = 0
    if vendor and vendor.firm_size_category:
        if 'Large' in vendor.firm_size_category:
            size_factor = 10  # Larger firms have more exposure
        elif 'Small' in vendor.firm_size_category:
            size_factor = -5  # Smaller firms may have less risk
    
    total_score = base_score + litigation_factor + federal_factor + size_factor
    return max(0, min(100, total_score))

def identify_risk_factors(litigation_cases):
    """Identify specific risk factors from litigation history"""
    risk_factors = []
    
    case_types = [case.get('case_name', '').lower() for case in litigation_cases]
    combined_text = ' '.join(case_types)
    
    if 'malpractice' in combined_text:
        risk_factors.append('Professional malpractice history')
    if 'breach' in combined_text:
        risk_factors.append('Contract breach allegations')
    if 'employment' in combined_text or 'discrimination' in combined_text:
        risk_factors.append('Employment law issues')
    if 'securities' in combined_text or 'fraud' in combined_text:
        risk_factors.append('Securities or fraud allegations')
    
    return risk_factors

def get_risk_recommendation(risk_score):
    """Get recommendation based on risk score"""
    if risk_score >= 80:
        return "High Risk - Conduct thorough due diligence and consider additional oversight"
    elif risk_score >= 60:
        return "Medium Risk - Review recent cases and monitor performance closely"
    elif risk_score >= 40:
        return "Low-Medium Risk - Standard monitoring recommended"
    else:
        return "Low Risk - Normal engagement procedures"

def analyze_case_trends(cases):
    """Analyze trends in case data"""
    if not cases:
        return []
    
    # Group cases by month for trend analysis
    monthly_counts = {}
    for case in cases:
        date_filed = case.get('dateFiled', '')
        if date_filed:
            try:
                month_key = date_filed[:7]  # YYYY-MM format
                monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
            except:
                continue
    
    # Convert to trend data
    trends = []
    for month, count in sorted(monthly_counts.items()):
        trends.append({
            'period': month,
            'case_count': count
        })
    
    return trends[-12:]  # Last 12 months

def calculate_avg_duration(cases):
    """Calculate average case duration (simplified)"""
    # This is a simplified calculation
    # In reality, you'd need to track case closure dates
    return "8-12 months (estimated)"
