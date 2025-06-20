"""
Legal Intelligence API Routes for LAIT
Provides endpoints for legal research and competitive intelligence using CourtListener
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
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
@jwt_required()
def verify_attorney():
    """Verify attorney credentials and get background information"""
    try:
        data = request.get_json()
        attorney_name = data.get('attorney_name')
        law_firm = data.get('law_firm')
        
        if not attorney_name:
            return jsonify({'error': 'Attorney name is required'}), 400
        
        verification_result = legal_service.verify_attorney_credentials(
            attorney_name, law_firm
        )
        
        return jsonify(verification_result)
        
    except Exception as e:
        return jsonify({'error': f'Error verifying attorney: {str(e)}'}), 500

@legal_intel_bp.route('/analyze-opposing-counsel', methods=['POST'])
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
