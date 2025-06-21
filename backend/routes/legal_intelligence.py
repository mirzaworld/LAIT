"""
Legal Intelligence API Routes for LAIT
Provides endpoints for legal research and competitive intelligence using CourtListener
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.dev_auth import development_jwt_required
from backend.services.courtlistener_service import LegalIntelligenceService
from backend.db.database import get_db_session
from backend.models.db_models import Vendor, Invoice, Matter
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

legal_intel_bp = Blueprint('legal_intelligence', __name__)

# Initialize the legal intelligence service
# API token should be stored in environment variables
COURTLISTENER_API_TOKEN = os.getenv('COURTLISTENER_API_TOKEN')
legal_service = LegalIntelligenceService(COURTLISTENER_API_TOKEN)

@legal_intel_bp.route('/verify-attorney', methods=['POST'])
@development_jwt_required
def verify_attorney():
    """Verify attorney credentials using trained attorney database and CourtListener"""
    try:
        data = request.get_json()
        attorney_name = data.get('attorney_name')
        law_firm = data.get('law_firm')
        bar_number = data.get('bar_number')
        
        if not attorney_name:
            return jsonify({'error': 'Attorney name is required'}), 400
        
        # First check our trained attorney database
        verification_result = verify_attorney_from_database(attorney_name, bar_number)
        
        # If found in our database, return that result
        if verification_result.get('verified'):
            return jsonify(verification_result)
        
        # Otherwise, check CourtListener
        courtlistener_result = legal_service.verify_attorney_credentials(
            attorney_name, law_firm
        )
        
        # Combine results
        combined_result = {
            'verified': courtlistener_result.get('verified', False),
            'attorney_name': attorney_name,
            'law_firm': law_firm,
            'bar_number': bar_number,
            'verification_sources': ['CourtListener API'],
            'attorney_info': courtlistener_result.get('attorney_info', {}),
            'confidence': 'medium' if courtlistener_result.get('verified') else 'low',
            'verification_date': datetime.utcnow().isoformat()
        }
        
        # Add bar verification if bar number provided
        if bar_number:
            bar_verification = verify_bar_number(bar_number, attorney_name)
            combined_result['bar_verification'] = bar_verification
            if bar_verification.get('valid'):
                combined_result['verification_sources'].append('Bar Database')
                combined_result['confidence'] = 'high'
        
        return jsonify(combined_result)
        
    except Exception as e:
        logger.error(f"Error verifying attorney: {str(e)}")
        return jsonify({'error': f'Error verifying attorney: {str(e)}'}), 500

def verify_attorney_from_database(attorney_name: str, bar_number: str = None) -> dict:
    """Verify attorney against our trained database"""
    import json
    import os
    
    try:
        # Load attorney database
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'ml', 'models')
        attorney_db_path = os.path.join(models_dir, 'attorney_database.json')
        
        if not os.path.exists(attorney_db_path):
            return {'verified': False, 'source': 'database_not_found'}
        
        with open(attorney_db_path, 'r') as f:
            attorney_db = json.load(f)
        
        # Search for attorney
        name_lower = attorney_name.lower()
        
        matches = []
        for attorney in attorney_db:
            attorney_name_lower = attorney.get('full_name', '').lower()
            
            # Exact name match
            if name_lower == attorney_name_lower:
                matches.append(attorney)
            # Partial name match
            elif any(part in attorney_name_lower for part in name_lower.split()):
                matches.append(attorney)
        
        # Check bar number if provided
        if bar_number:
            bar_matches = [a for a in attorney_db if a.get('bar_number') == bar_number]
            if bar_matches:
                return {
                    'verified': True,
                    'source': 'attorney_database',
                    'attorney_info': bar_matches[0],
                    'match_type': 'bar_number'
                }
        
        # Return best match
        if matches:
            return {
                'verified': True,
                'source': 'attorney_database',
                'attorney_info': matches[0],
                'match_type': 'name_match'
            }
        
        return {'verified': False, 'source': 'not_found_in_database'}
        
    except Exception as e:
        logger.error(f"Error checking attorney database: {str(e)}")
        return {'verified': False, 'error': str(e)}

def verify_bar_number(bar_number: str, attorney_name: str = None) -> dict:
    """Verify bar number format and authenticity"""
    # Basic bar number format validation
    if not bar_number or len(bar_number) < 5:
        return {'valid': False, 'reason': 'Invalid bar number format'}
    
    # Extract state from bar number (first 2-3 characters typically)
    state_code = bar_number[:2].upper()
    
    # Valid state codes
    valid_states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI', 'NJ', 'VA', 'WA', 'AZ', 'MA']
    
    if state_code not in valid_states:
        return {'valid': False, 'reason': 'Unrecognized state code in bar number'}
    
    # Basic number validation
    number_part = bar_number[2:]
    if not number_part.isdigit():
        return {'valid': False, 'reason': 'Invalid number format in bar number'}
    
    return {
        'valid': True,
        'state': state_code,
        'number': number_part,
        'format_valid': True
    }
    
    # Mock validation based on common bar number patterns
    state_patterns = {
        'CA': r'^CA\d{6}$',
        'NY': r'^NY\d{7}$',
        'TX': r'^TX\d{8}$',
        'FL': r'^FL\d{7}$'
    }
    
    import re
    for state, pattern in state_patterns.items():
        if re.match(pattern, bar_number):
            return {
                'valid': True,
                'state': state,
                'format_valid': True,
                'status': 'Active',
                'verification_method': 'Format validation',
                'note': 'Full verification requires state bar API integration'
            }
    
    # Check if it's a numeric format (common for many states)
    if bar_number.isdigit() and len(bar_number) >= 5:
        return {
            'valid': True,
            'format_valid': True,
            'status': 'Unknown',
            'verification_method': 'Numeric format validation',
            'note': 'State cannot be determined from number alone'
        }
    
    return {'valid': False, 'reason': 'Unrecognized format'}

@legal_intel_bp.route('/analyze-opposing-counsel', methods=['POST'])
@development_jwt_required
def analyze_opposing_counsel():
    """Analyze opposing counsel for strategic insights"""
    try:
        data = request.get_json()
        attorney_name = data.get('attorney_name')
        law_firm = data.get('law_firm')
        matter_id = data.get('matter_id')  # Optional: to save insights to specific matter
        
        if not attorney_name:
            return jsonify({'error': 'Attorney name is required'}), 400
        
        analysis = legal_service.analyze_opposing_counsel(attorney_name, law_firm)
        
        # If matter_id provided, save insights to matter record
        if matter_id:
            session = get_db_session()
            try:
                matter = session.query(Matter).get(matter_id)
                if matter:
                    # Store analysis in matter's additional info
                    if not matter.additional_info:
                        matter.additional_info = {}
                    
                    matter.additional_info['opposing_counsel_analysis'] = {
                        'attorney_name': attorney_name,
                        'law_firm': law_firm,
                        'analysis': analysis,
                        'analyzed_at': datetime.utcnow().isoformat()
                    }
                    session.commit()
            except Exception as e:
                session.rollback()
                print(f"Error saving analysis to matter: {str(e)}")
            finally:
                session.close()
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': f'Error analyzing opposing counsel: {str(e)}'}), 500

@legal_intel_bp.route('/estimate-case-complexity', methods=['POST'])
@development_jwt_required
def estimate_case_complexity():
    """Estimate case complexity based on similar cases"""
    try:
        data = request.get_json()
        case_description = data.get('case_description')
        court = data.get('court')
        matter_id = data.get('matter_id')
        
        if not case_description:
            return jsonify({'error': 'Case description is required'}), 400
        
        complexity_analysis = legal_service.estimate_case_complexity(
            case_description, court
        )
        
        # If matter_id provided, save complexity estimate
        if matter_id:
            session = get_db_session()
            try:
                matter = session.query(Matter).get(matter_id)
                if matter:
                    if not matter.additional_info:
                        matter.additional_info = {}
                    
                    matter.additional_info['complexity_analysis'] = {
                        'case_description': case_description,
                        'court': court,
                        'analysis': complexity_analysis,
                        'analyzed_at': datetime.utcnow().isoformat()
                    }
                    
                    # Update matter risk score based on complexity
                    if complexity_analysis.get('complexity_score'):
                        complexity_score = complexity_analysis['complexity_score']
                        # Convert 1-10 scale to risk multiplier
                        risk_multiplier = 1 + (complexity_score - 5) * 0.1
                        matter.risk_multiplier = risk_multiplier
                    
                    session.commit()
            except Exception as e:
                session.rollback()
                print(f"Error saving complexity analysis: {str(e)}")
            finally:
                session.close()
        
        return jsonify(complexity_analysis)
        
    except Exception as e:
        return jsonify({'error': f'Error estimating case complexity: {str(e)}'}), 500

@legal_intel_bp.route('/judge-insights', methods=['POST'])
@development_jwt_required
def get_judge_insights():
    """Get insights about a judge for case strategy"""
    try:
        data = request.get_json()
        judge_name = data.get('judge_name')
        matter_id = data.get('matter_id')
        
        if not judge_name:
            return jsonify({'error': 'Judge name is required'}), 400
        
        judge_insights = legal_service.get_judge_insights(judge_name)
        
        # If matter_id provided, save judge insights
        if matter_id:
            session = get_db_session()
            try:
                matter = session.query(Matter).get(matter_id)
                if matter:
                    if not matter.additional_info:
                        matter.additional_info = {}
                    
                    matter.additional_info['judge_insights'] = {
                        'judge_name': judge_name,
                        'insights': judge_insights,
                        'analyzed_at': datetime.utcnow().isoformat()
                    }
                    session.commit()
            except Exception as e:
                session.rollback()
                print(f"Error saving judge insights: {str(e)}")
            finally:
                session.close()
        
        return jsonify(judge_insights)
        
    except Exception as e:
        return jsonify({'error': f'Error getting judge insights: {str(e)}'}), 500

@legal_intel_bp.route('/vendor-verification', methods=['POST'])
@development_jwt_required
def verify_vendor_attorneys():
    """Verify attorneys at a vendor law firm"""
    try:
        data = request.get_json()
        vendor_id = data.get('vendor_id')
        
        if not vendor_id:
            return jsonify({'error': 'Vendor ID is required'}), 400
        
        session = get_db_session()
        try:
            vendor = session.query(Vendor).get(vendor_id)
            if not vendor:
                return jsonify({'error': 'Vendor not found'}), 404
            
            # Verify key attorneys at the firm
            verification_results = []
            
            # Try to find attorneys at this firm
            # This is a simplified approach - in practice you'd have a list of key attorneys
            firm_analysis = legal_service.client.analyze_law_firm(vendor.name)
            
            for attorney in firm_analysis.attorneys[:5]:  # Check top 5 attorneys
                verification = legal_service.verify_attorney_credentials(
                    attorney.name, vendor.name
                )
                verification_results.append({
                    'attorney_name': attorney.name,
                    'verification': verification
                })
            
            # Update vendor with verification status
            if not vendor.additional_info:
                vendor.additional_info = {}
            
            vendor.additional_info['attorney_verification'] = {
                'verified_attorneys': verification_results,
                'firm_analysis': {
                    'total_attorneys': len(firm_analysis.attorneys),
                    'total_cases': firm_analysis.total_cases,
                    'practice_areas': firm_analysis.practice_areas,
                    'success_metrics': firm_analysis.success_metrics
                },
                'verified_at': datetime.utcnow().isoformat()
            }
            
            session.commit()
            
            return jsonify({
                'vendor_id': vendor_id,
                'vendor_name': vendor.name,
                'verification_results': verification_results,
                'firm_analysis': {
                    'total_attorneys': len(firm_analysis.attorneys),
                    'total_cases': firm_analysis.total_cases,
                    'practice_areas': firm_analysis.practice_areas[:10],  # Top 10
                    'courts_appeared': firm_analysis.courts_appeared[:10],  # Top 10
                    'success_metrics': firm_analysis.success_metrics
                }
            })
            
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
        
    except Exception as e:
        return jsonify({'error': f'Error verifying vendor attorneys: {str(e)}'}), 500

@legal_intel_bp.route('/competitive-landscape', methods=['GET'])
@development_jwt_required
def get_competitive_landscape():
    """Get competitive landscape analysis for a practice area"""
    try:
        practice_area = request.args.get('practice_area')
        location = request.args.get('location')
        
        if not practice_area:
            return jsonify({'error': 'Practice area is required'}), 400
        
        session = get_db_session()
        try:
            # Get vendors in this practice area
            vendors_query = session.query(Vendor)\
                .filter(Vendor.practice_area == practice_area)
            
            if location:
                vendors_query = vendors_query.filter(
                    (Vendor.city.ilike(f'%{location}%')) |
                    (Vendor.state_province.ilike(f'%{location}%'))
                )
            
            vendors = vendors_query.limit(20).all()
            
            competitive_analysis = []
            
            for vendor in vendors:
                # Basic vendor info
                vendor_info = {
                    'vendor_id': vendor.id,
                    'name': vendor.name,
                    'firm_size_category': vendor.firm_size_category,
                    'location': f"{vendor.city}, {vendor.state_province}",
                    'total_spend': vendor.total_spend or 0,
                    'performance_score': vendor.performance_score
                }
                
                # Add CourtListener data if available
                if vendor.additional_info and 'attorney_verification' in vendor.additional_info:
                    firm_analysis = vendor.additional_info['attorney_verification'].get('firm_analysis', {})
                    vendor_info.update({
                        'courtlistener_data': {
                            'total_cases': firm_analysis.get('total_cases', 0),
                            'practice_areas': firm_analysis.get('practice_areas', []),
                            'success_metrics': firm_analysis.get('success_metrics', {})
                        }
                    })
                
                competitive_analysis.append(vendor_info)
            
            # Sort by total spend and performance
            competitive_analysis.sort(
                key=lambda x: (x.get('total_spend', 0), x.get('performance_score', 0)), 
                reverse=True
            )
            
            return jsonify({
                'practice_area': practice_area,
                'location': location,
                'total_vendors': len(competitive_analysis),
                'competitive_landscape': competitive_analysis
            })
            
        finally:
            session.close()
        
    except Exception as e:
        return jsonify({'error': f'Error getting competitive landscape: {str(e)}'}), 500

@legal_intel_bp.route('/matter-research', methods=['POST'])
@development_jwt_required
def research_matter():
    """Comprehensive research for a matter using multiple CourtListener endpoints"""
    try:
        data = request.get_json()
        matter_id = data.get('matter_id')
        research_type = data.get('research_type', 'comprehensive')  # comprehensive, opposing_counsel, complexity, judge
        
        if not matter_id:
            return jsonify({'error': 'Matter ID is required'}), 400
        
        session = get_db_session()
        try:
            matter = session.query(Matter).get(matter_id)
            if not matter:
                return jsonify({'error': 'Matter not found'}), 404
            
            research_results = {
                'matter_id': matter_id,
                'matter_name': matter.name,
                'research_type': research_type,
                'research_timestamp': datetime.utcnow().isoformat(),
                'results': {}
            }
            
            # Complexity analysis if description available
            if matter.description and research_type in ['comprehensive', 'complexity']:
                complexity_analysis = legal_service.estimate_case_complexity(
                    matter.description, matter.court
                )
                research_results['results']['complexity_analysis'] = complexity_analysis
            
            # Judge insights if judge information available
            if hasattr(matter, 'judge_name') and matter.judge_name and research_type in ['comprehensive', 'judge']:
                judge_insights = legal_service.get_judge_insights(matter.judge_name)
                research_results['results']['judge_insights'] = judge_insights
            
            # Save research results to matter
            if not matter.additional_info:
                matter.additional_info = {}
            
            matter.additional_info['legal_research'] = research_results
            session.commit()
            
            return jsonify(research_results)
            
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
        
    except Exception as e:
        return jsonify({'error': f'Error researching matter: {str(e)}'}), 500

@legal_intel_bp.route('/search-precedents', methods=['POST'])
@development_jwt_required
def search_legal_precedents():
    """Search for legal precedents relevant to a case"""
    try:
        data = request.get_json()
        search_query = data.get('search_query')
        court = data.get('court')
        matter_id = data.get('matter_id')
        
        if not search_query:
            return jsonify({'error': 'Search query is required'}), 400
        
        similar_cases = legal_service.client.search_similar_cases(
            search_query, court, 20
        )
        
        # If matter_id provided, save precedents
        if matter_id:
            session = get_db_session()
            try:
                matter = session.query(Matter).get(matter_id)
                if matter:
                    if not matter.additional_info:
                        matter.additional_info = {}
                    
                    if 'legal_research' not in matter.additional_info:
                        matter.additional_info['legal_research'] = {}
                    
                    matter.additional_info['legal_research']['precedents'] = {
                        'search_query': search_query,
                        'court': court,
                        'similar_cases': similar_cases,
                        'searched_at': datetime.utcnow().isoformat()
                    }
                    session.commit()
            except Exception as e:
                session.rollback()
                print(f"Error saving precedents: {str(e)}")
            finally:
                session.close()
        
        return jsonify({
            'search_query': search_query,
            'court': court,
            'total_results': len(similar_cases),
            'similar_cases': similar_cases
        })
        
    except Exception as e:
        return jsonify({'error': f'Error searching precedents: {str(e)}'}), 500

@legal_intel_bp.route('/comprehensive-research', methods=['POST'])
@development_jwt_required
def comprehensive_case_research():
    """Comprehensive case research using multiple CourtListener endpoints"""
    try:
        data = request.get_json()
        case_description = data.get('case_description')
        court = data.get('court')
        matter_id = data.get('matter_id')
        
        if not case_description:
            return jsonify({'error': 'Case description is required'}), 400
        
        research_results = legal_service.comprehensive_case_research(
            case_description, court
        )
        
        # Save to matter if matter_id provided
        if matter_id:
            session = get_db_session()
            try:
                matter = session.query(Matter).get(matter_id)
                if matter:
                    if not matter.additional_info:
                        matter.additional_info = {}
                    
                    matter.additional_info['comprehensive_research'] = research_results
                    session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"Error saving research: {str(e)}")
            finally:
                session.close()
        
        return jsonify(research_results)
        
    except Exception as e:
        return jsonify({'error': f'Error in comprehensive research: {str(e)}'}), 500

@legal_intel_bp.route('/judge-patterns', methods=['POST'])
@development_jwt_required
def analyze_judge_patterns():
    """Analyze patterns in a judge's decisions and case management"""
    try:
        data = request.get_json()
        judge_name = data.get('judge_name')
        matter_id = data.get('matter_id')
        
        if not judge_name:
            return jsonify({'error': 'Judge name is required'}), 400
        
        analysis = legal_service.analyze_judge_patterns(judge_name)
        
        # Save to matter if matter_id provided
        if matter_id:
            session = get_db_session()
            try:
                matter = session.query(Matter).get(matter_id)
                if matter:
                    if not matter.additional_info:
                        matter.additional_info = {}
                    
                    matter.additional_info['judge_pattern_analysis'] = analysis
                    session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"Error saving judge analysis: {str(e)}")
            finally:
                session.close()
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': f'Error analyzing judge patterns: {str(e)}'}), 500

@legal_intel_bp.route('/competitive-analysis', methods=['POST'])
@development_jwt_required
def competitive_firm_analysis():
    """Compare multiple law firms using CourtListener data"""
    try:
        data = request.get_json()
        firm_names = data.get('firm_names', [])
        practice_area = data.get('practice_area')
        
        if not firm_names or len(firm_names) < 2:
            return jsonify({'error': 'At least 2 firm names are required for comparison'}), 400
        
        analysis = legal_service.competitive_firm_analysis(firm_names, practice_area)
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': f'Error in competitive analysis: {str(e)}'}), 500

@legal_intel_bp.route('/precedent-research', methods=['POST'])
@development_jwt_required
def legal_precedent_research():
    """Research legal precedents for a specific issue"""
    try:
        data = request.get_json()
        legal_issue = data.get('legal_issue')
        jurisdiction = data.get('jurisdiction')
        matter_id = data.get('matter_id')
        
        if not legal_issue:
            return jsonify({'error': 'Legal issue description is required'}), 400
        
        research = legal_service.legal_precedent_research(legal_issue, jurisdiction)
        
        # Save to matter if matter_id provided
        if matter_id:
            session = get_db_session()
            try:
                matter = session.query(Matter).get(matter_id)
                if matter:
                    if not matter.additional_info:
                        matter.additional_info = {}
                    
                    matter.additional_info['precedent_research'] = research
                    session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"Error saving precedent research: {str(e)}")
            finally:
                session.close()
        
        return jsonify(research)
        
    except Exception as e:
        return jsonify({'error': f'Error in precedent research: {str(e)}'}), 500

@legal_intel_bp.route('/court-analytics', methods=['GET'])
@development_jwt_required
def get_court_analytics():
    """Analyze court statistics and patterns"""
    try:
        court_identifier = request.args.get('court_id')
        
        if not court_identifier:
            return jsonify({'error': 'Court identifier is required'}), 400
        
        analytics = legal_service.court_analytics(court_identifier)
        
        return jsonify(analytics)
        
    except Exception as e:
        return jsonify({'error': f'Error in court analytics: {str(e)}'}), 500

@legal_intel_bp.route('/courts/search', methods=['GET'])
@development_jwt_required
def search_courts():
    """Search for courts by jurisdiction and level"""
    try:
        jurisdiction = request.args.get('jurisdiction')
        level = request.args.get('level')
        
        courts = legal_service.client.search_courts(jurisdiction, level)
        
        return jsonify({
            'total_results': len(courts),
            'courts': courts
        })
        
    except Exception as e:
        return jsonify({'error': f'Error searching courts: {str(e)}'}), 500

@legal_intel_bp.route('/audio-recordings', methods=['GET'])
@development_jwt_required
def search_audio_recordings():
    """Search for oral argument audio recordings"""
    try:
        case_name = request.args.get('case_name')
        court = request.args.get('court')
        
        recordings = legal_service.client.search_audio_recordings(case_name, court)
        
        return jsonify({
            'total_results': len(recordings),
            'recordings': recordings
        })
        
    except Exception as e:
        return jsonify({'error': f'Error searching audio recordings: {str(e)}'}), 500

@legal_intel_bp.route('/docket/<int:docket_id>/entries', methods=['GET'])
@development_jwt_required
def get_docket_entries():
    """Get docket entries (filings) for a specific case"""
    try:
        docket_id = request.view_args['docket_id']
        limit = request.args.get('limit', 50, type=int)
        
        entries = legal_service.client.get_docket_entries(docket_id, limit)
        
        return jsonify({
            'docket_id': docket_id,
            'total_entries': len(entries),
            'entries': entries
        })
        
    except Exception as e:
        return jsonify({'error': f'Error getting docket entries: {str(e)}'}), 500

@legal_intel_bp.route('/citations/<int:opinion_id>', methods=['GET'])
@development_jwt_required
def get_citation_network():
    """Get citation network for a specific opinion"""
    try:
        opinion_id = request.view_args['opinion_id']
        
        citing_cases = legal_service.client.search_citing_cases(opinion_id)
        cited_cases = legal_service.client.search_cited_cases(opinion_id)
        
        return jsonify({
            'opinion_id': opinion_id,
            'citation_network': {
                'cited_by': citing_cases,
                'cites': cited_cases,
                'citation_impact': len(citing_cases)
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error getting citation network: {str(e)}'}), 500

@legal_intel_bp.route('/bulk-research', methods=['POST'])
@development_jwt_required
def bulk_legal_research():
    """Perform bulk research for multiple matters or cases"""
    try:
        data = request.get_json()
        research_items = data.get('research_items', [])  # List of research requests
        research_type = data.get('research_type', 'precedents')  # precedents, complexity, judges
        
        if not research_items:
            return jsonify({'error': 'Research items are required'}), 400
        
        bulk_results = {
            'research_type': research_type,
            'total_items': len(research_items),
            'results': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        for item in research_items[:10]:  # Limit to 10 items to avoid API rate limits
            if research_type == 'precedents':
                result = legal_service.legal_precedent_research(
                    item.get('legal_issue', ''),
                    item.get('jurisdiction')
                )
            elif research_type == 'complexity':
                result = legal_service.estimate_case_complexity(
                    item.get('case_description', ''),
                    item.get('court')
                )
            elif research_type == 'comprehensive':
                result = legal_service.comprehensive_case_research(
                    item.get('case_description', ''),
                    item.get('court')
                )
            else:
                result = {'error': 'Invalid research type'}
            
            bulk_results['results'].append({
                'item_id': item.get('id', ''),
                'research_result': result
            })
        
        return jsonify(bulk_results)
        
    except Exception as e:
        return jsonify({'error': f'Error in bulk research: {str(e)}'}), 500

# Add the missing endpoints that the frontend expects

@legal_intel_bp.route('/search-cases', methods=['POST'])
@development_jwt_required
def search_cases():
    """Search for legal cases using real case database and CourtListener API"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        court = data.get('court')
        date_range = data.get('date_range')
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # First search our local case database
        local_cases = search_local_case_database(query, court)
        
        # Then search CourtListener API if available
        api_cases = []
        try:
            search_results = legal_service.search_case_law(query, court=court, limit=10)
            for case in search_results.get('results', []):
                api_cases.append({
                    'id': str(case.get('id', '')),
                    'title': case.get('caseName', case.get('case_name', 'Unknown Case')),
                    'court': case.get('court', 'Unknown Court'),
                    'date': case.get('dateFiled', case.get('date_filed', '')),
                    'relevance': case.get('score', 85),
                    'excerpt': case.get('snippet', case.get('text', ''))[:200] + '...',
                    'citation': case.get('citation', ''),
                    'url': case.get('absolute_url', ''),
                    'source': 'CourtListener'
                })
        except Exception as e:
            logger.warning(f"CourtListener API unavailable: {str(e)}")
        
        # Combine results
        all_cases = local_cases + api_cases
        
        return jsonify({
            'cases': all_cases[:20],  # Limit to 20 results
            'total': len(all_cases),
            'query': query,
            'court': court,
            'sources': ['Local Database', 'CourtListener API'] if api_cases else ['Local Database']
        })
        
    except Exception as e:
        logger.error(f"Error searching cases: {str(e)}")
        return jsonify({'error': f'Error searching cases: {str(e)}'}), 500

def search_local_case_database(query: str, court: str = None) -> list:
    """Search the local case database"""
    import json
    import os
    
    try:
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'ml', 'models')
        case_db_path = os.path.join(models_dir, 'case_database.json')
        
        if not os.path.exists(case_db_path):
            return []
        
        with open(case_db_path, 'r') as f:
            case_db = json.load(f)
        
        query_lower = query.lower()
        matched_cases = []
        
        for case in case_db:
            # Search in title, description, and case type
            title = case.get('title', '').lower()
            description = case.get('description', '').lower()
            case_type = case.get('case_type', '').lower()
            court_name = case.get('court', '').lower()
            
            # Calculate relevance score
            relevance = 0
            if query_lower in title:
                relevance += 30
            if query_lower in description:
                relevance += 20
            if query_lower in case_type:
                relevance += 25
            if any(word in title or word in description for word in query_lower.split()):
                relevance += 15
            
            # Filter by court if specified
            if court and court.lower() not in court_name:
                continue
                
            if relevance > 0:
                matched_cases.append({
                    'id': case.get('case_id', ''),
                    'title': case.get('title', 'Unknown Case'),
                    'court': case.get('court', 'Unknown Court'),
                    'date': case.get('filing_date', ''),
                    'relevance': relevance,
                    'excerpt': case.get('description', '')[:200] + '...',
                    'case_type': case.get('case_type', ''),
                    'status': case.get('status', ''),
                    'source': 'Local Database'
                })
        
        # Sort by relevance
        matched_cases.sort(key=lambda x: x['relevance'], reverse=True)
        return matched_cases[:10]  # Return top 10 matches
        
    except Exception as e:
        logger.error(f"Error searching local case database: {str(e)}")
        return []

@legal_intel_bp.route('/vendor-risk-assessment', methods=['POST'])
@development_jwt_required
def vendor_risk_assessment():
    """Assess vendor risk based on legal intelligence"""
    try:
        data = request.get_json()
        vendor_name = data.get('vendor_name')
        
        if not vendor_name:
            return jsonify({'error': 'Vendor name is required'}), 400
        
        # Get vendor from database
        session = get_db_session()
        try:
            vendor = session.query(Vendor).filter(
                Vendor.name.ilike(f'%{vendor_name}%')
            ).first()
            
            if not vendor:
                return jsonify({'error': 'Vendor not found'}), 404
            
            # Perform comprehensive risk assessment
            risk_assessment = legal_service.assess_vendor_risk(vendor_name)
            
            # Calculate risk factors based on vendor data
            risk_factors = []
            risk_score = 0
            
            # Check for legal issues in vendor intelligence
            if hasattr(vendor, 'legal_status') and vendor.legal_status:
                if 'litigation' in vendor.legal_status.lower():
                    risk_factors.append('Active litigation identified')
                    risk_score += 30
                if 'bankruptcy' in vendor.legal_status.lower():
                    risk_factors.append('Bankruptcy history')
                    risk_score += 40
                if 'regulatory' in vendor.legal_status.lower():
                    risk_factors.append('Regulatory violations')
                    risk_score += 25
            
            # Check financial indicators
            if hasattr(vendor, 'financial_rating') and vendor.financial_rating:
                if vendor.financial_rating.lower() in ['poor', 'high risk']:
                    risk_factors.append('Poor financial rating')
                    risk_score += 20
            
            # Default to low risk if no issues found
            if risk_score == 0:
                risk_factors.append('Clean legal record')
                risk_factors.append('No known litigation')
                risk_score = 15
            
            # Determine risk level
            if risk_score >= 60:
                risk_level = 'high'
            elif risk_score >= 30:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            assessment_result = {
                'vendor': vendor_name,
                'riskLevel': risk_level,
                'score': risk_score,
                'factors': risk_factors,
                'details': risk_assessment,
                'assessed_at': datetime.utcnow().isoformat()
            }
            
            return jsonify({
                'assessments': [assessment_result],
                'total': 1,
                'vendor_name': vendor_name
            })
            
        finally:
            session.close()
        
    except Exception as e:
        logger.error(f"Error assessing vendor risk: {str(e)}")
        return jsonify({'error': f'Error assessing vendor risk: {str(e)}'}), 500

@legal_intel_bp.route('/case-details/<string:case_id>', methods=['GET'])
@development_jwt_required
def get_case_details(case_id):
    """Get detailed information about a specific legal case"""
    try:
        # Check if it's a local database case ID (starts with CASE-)
        if case_id.startswith('CASE-'):
            # Get case details from local database
            case_details = get_case_from_local_database(case_id)
            if case_details:
                return jsonify(case_details)
            else:
                return jsonify({'error': 'Case not found in local database'}), 404
        
        # Try to get opinion details from CourtListener (numeric ID)
        try:
            case_details = legal_service.client.get_opinion_detail(int(case_id))
        except ValueError:
            return jsonify({'error': 'Invalid case ID format'}), 400
        
        if not case_details:
            return jsonify({'error': 'Case not found'}), 404
        
        # Format the detailed case information
        formatted_details = {
            'id': case_details.get('id', case_id),
            'title': case_details.get('case_name', 'Unknown Case'),
            'court': case_details.get('court', 'Unknown Court'),
            'date_filed': case_details.get('date_filed', ''),
            'date_created': case_details.get('date_created', ''),
            'judges': case_details.get('judges', []),
            'citation': case_details.get('citation', ''),
            'full_text': case_details.get('plain_text', case_details.get('html_with_citations', '')),
            'summary': case_details.get('summary', ''),
            'type': case_details.get('type', ''),
            'status': case_details.get('status', ''),
            'precedential_status': case_details.get('precedential_status', ''),
            'docket_number': case_details.get('docket_number', ''),
            'source': 'CourtListener',
            'url': case_details.get('absolute_url', ''),
            'download_url': case_details.get('download_url', ''),
            'local_path': case_details.get('local_path', ''),
            # Additional metadata
            'cluster': case_details.get('cluster', {}),
            'extracted_by_ocr': case_details.get('extracted_by_ocr', False),
            'page_count': case_details.get('page_count', 0),
            'author': case_details.get('author', {}),
            'joined_by': case_details.get('joined_by', []),
            'per_curiam': case_details.get('per_curiam', False),
            'opinions_cited': case_details.get('opinions_cited', []),
        }
        
        return jsonify(formatted_details)
        
    except ValueError:
        # Case ID is not a valid integer, return error
        return jsonify({'error': 'Invalid case ID format'}), 400
    except Exception as e:
        logger.error(f"Error getting case details for case {case_id}: {str(e)}")
        return jsonify({'error': f'Error retrieving case details: {str(e)}'}), 500

@legal_intel_bp.route('/case-details/<case_id>', methods=['GET'])
@development_jwt_required
def get_case_details(case_id):
    """Get detailed information about a specific case"""
    try:
        # First try to get from local database
        case_details = get_case_from_local_database(case_id)
        
        if case_details:
            return jsonify(case_details)
        
        # If not found locally, try CourtListener API
        try:
            api_case = legal_service.get_case_details(case_id)
            if api_case:
                return jsonify({
                    'id': case_id,
                    'title': api_case.get('caseName', 'Unknown Case'),
                    'court': api_case.get('court', 'Unknown Court'),
                    'date': api_case.get('dateFiled', ''),
                    'status': api_case.get('status', 'Unknown'),
                    'description': api_case.get('summary', api_case.get('text', 'No description available')),
                    'citation': api_case.get('citation', ''),
                    'judges': api_case.get('judges', []),
                    'attorneys': api_case.get('attorneys', []),
                    'source': 'CourtListener API',
                    'url': api_case.get('absolute_url', '')
                })
        except Exception as e:
            logger.warning(f"CourtListener API error: {str(e)}")
        
        # If not found anywhere, return a structured response
        return jsonify({
            'id': case_id,
            'title': f"Case {case_id}",
            'court': 'Court information not available',
            'date': 'Date not available',
            'status': 'Status unknown',
            'description': 'Case details are not available in the current database. This case may require additional research or may not exist in our current data sources.',
            'source': 'Not found',
            'error': 'Case not found in available databases'
        }), 404
        
    except Exception as e:
        logger.error(f"Error getting case details: {str(e)}")
        return jsonify({'error': f'Error retrieving case details: {str(e)}'}), 500

def get_case_from_local_database(case_id: str) -> dict:
    """Get case details from local database"""
    import json
    import os
    
    try:
        # Load case data from our trained dataset
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'ml', 'models')
        case_db_path = os.path.join(models_dir, 'case_database.json')
        
        if os.path.exists(case_db_path):
            with open(case_db_path, 'r') as f:
                cases = json.load(f)
            
            # Find the case by ID
            for case in cases:
                if case.get('case_id') == case_id:
                    return {
                        'id': case.get('case_id'),
                        'title': case.get('title'),
                        'court': case.get('court'),
                        'date': case.get('filing_date'),
                        'status': case.get('status'),
                        'case_type': case.get('case_type'),
                        'excerpt': case.get('description'),
                        'full_text': case.get('description', ''),
                        'relevance': 100,
                        'source': 'Local Database',
                        'attorneys': case.get('attorneys', []),
                        'judges': case.get('judges', []),
                        'citation': case.get('citation', ''),
                        'docket_number': case.get('docket_number', ''),
                        'practice_areas': case.get('practice_areas', []),
                        'outcome': case.get('outcome', case.get('resolution', '')),
                        'damages': case.get('damages_amount', 0),
                        'precedential_value': case.get('precedential_value', 'Medium'),
                        'complexity': case.get('complexity', 'Medium'),
                        'duration_days': case.get('duration_days', 0),
                        'cost_estimate': case.get('cost_estimate', 0)
                    }
        
        return None
    except Exception as e:
        logger.error(f"Error getting case from local database: {str(e)}")
        return None
