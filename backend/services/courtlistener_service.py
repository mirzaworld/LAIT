"""
CourtListener API Integration for LAIT Legal Spend Optimizer

Integrates with CourtListener API to provide:
- Attorney verification and background information
- Law firm case history and track records
- Judge and court information for matter planning
- Legal precedent research for cost estimation
- Competitive intelligence on opposing counsel
- Court records and docket information
- Case law research and citations
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from urllib.parse import urljoin, quote_plus
import time

logger = logging.getLogger(__name__)

@dataclass
class AttorneyInfo:
    """Attorney information from CourtListener"""
    id: int
    name: str
    bar_admissions: List[str]
    organizations: List[str]
    contact_info: Dict[str, Any]
    case_count: int
    specialties: List[str]

@dataclass
class LawFirmProfile:
    """Law firm profile aggregated from multiple attorneys"""
    name: str
    attorneys: List[AttorneyInfo]
    total_cases: int
    practice_areas: List[str]
    courts_appeared: List[str]
    recent_cases: List[Dict]
    success_metrics: Dict[str, float]

@dataclass
class DocketInfo:
    """Docket information from CourtListener"""
    id: int
    case_name: str
    docket_number: str
    court: str
    date_filed: str
    date_terminated: Optional[str]
    nature_of_suit: str
    cause: str
    jury_demand: str
    jurisdiction_type: str

@dataclass
class LawFirmAnalysis:
    """Law firm analysis results"""
    attorneys: List[AttorneyInfo]
    total_cases: int
    practice_areas: List[str]
    success_metrics: Dict[str, Any]
    recent_cases: List[Dict[str, Any]]

class CourtListenerClient:
    """Client for interacting with CourtListener API"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.base_url = "https://www.courtlistener.com/api/rest/v4/"
        self.api_token = api_token
        self.session = requests.Session()
        
        if api_token:
            self.session.headers.update({
                'Authorization': f'Token {api_token}'
            })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests for free tier
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a request to the CourtListener API"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.get(url, params=params or {}, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"CourtListener API request failed: {str(e)}")
            return {'results': [], 'count': 0}

    def search_courts(self, jurisdiction: str = None, level: str = None) -> List[Dict]:
        """Search for courts"""
        params = {'format': 'json'}
        
        if jurisdiction:
            params['jurisdiction'] = jurisdiction
        if level:
            params['level'] = level
        
        try:
            data = self._make_request('courts/', params)
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Error searching courts: {str(e)}")
            return []

    def get_court_info(self, court_id: str) -> Dict:
        """Get detailed information about a specific court"""
        try:
            data = self._make_request(f'courts/{court_id}/')
            return data
        except Exception as e:
            logger.error(f"Error getting court info: {str(e)}")
            return {}

    def search_dockets(self, case_name: str = None, court: str = None, 
                      date_filed_after: str = None, limit: int = 20) -> List[DocketInfo]:
        """Search for dockets (cases) with various filters"""
        params = {
            'format': 'json',
            'page_size': limit,
            'ordering': '-date_filed'
        }
        
        if case_name:
            params['case_name__icontains'] = case_name
        if court:
            params['court'] = court
        if date_filed_after:
            params['date_filed__gte'] = date_filed_after
            
        try:
            data = self._make_request('dockets/', params)
            dockets = []
            
            for docket_data in data.get('results', []):
                docket = DocketInfo(
                    id=docket_data.get('id'),
                    case_name=docket_data.get('case_name', ''),
                    docket_number=docket_data.get('docket_number', ''),
                    court=docket_data.get('court', {}).get('full_name', ''),
                    date_filed=docket_data.get('date_filed', ''),
                    date_terminated=docket_data.get('date_terminated'),
                    nature_of_suit=docket_data.get('nature_of_suit', ''),
                    cause=docket_data.get('cause', ''),
                    jury_demand=docket_data.get('jury_demand', ''),
                    jurisdiction_type=docket_data.get('jurisdiction_type', '')
                )
                dockets.append(docket)
            
            return dockets
        except Exception as e:
            logger.error(f"Error searching dockets: {str(e)}")
            return []

    def get_docket_entries(self, docket_id: int, limit: int = 50) -> List[Dict]:
        """Get docket entries for a specific case"""
        params = {
            'docket': docket_id,
            'format': 'json',
            'page_size': limit,
            'ordering': '-date_created'
        }
        
        try:
            data = self._make_request('docket-entries/', params)
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Error getting docket entries: {str(e)}")
            return []

    def search_opinions(self, query: str, court: str = None, limit: int = 20) -> List[Dict]:
        """Search for legal opinions"""
        params = {
            'q': query,
            'type': 'o',  # Opinions
            'format': 'json',
            'page_size': limit
        }
        
        if court:
            params['court'] = court
        
        try:
            data = self._make_request('search/', params)
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Error searching opinions: {str(e)}")
            return []

    def get_opinion_detail(self, opinion_id: int) -> Dict:
        """Get detailed information about a specific opinion"""
        try:
            data = self._make_request(f'opinions/{opinion_id}/')
            return data
        except Exception as e:
            logger.error(f"Error getting opinion detail: {str(e)}")
            return {}

    def search_cited_cases(self, opinion_id: int) -> List[Dict]:
        """Get cases cited by a specific opinion"""
        params = {
            'citing_opinion': opinion_id,
            'format': 'json'
        }
        
        try:
            data = self._make_request('citations/', params)
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Error searching cited cases: {str(e)}")
            return []

    def search_citing_cases(self, opinion_id: int) -> List[Dict]:
        """Get cases that cite a specific opinion"""
        params = {
            'cited_opinion': opinion_id,
            'format': 'json'
        }
        
        try:
            data = self._make_request('citations/', params)
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Error searching citing cases: {str(e)}")
            return []

    def search_audio_recordings(self, case_name: str = None, court: str = None) -> List[Dict]:
        """Search for oral argument audio recordings"""
        params = {'format': 'json'}
        
        if case_name:
            params['case_name__icontains'] = case_name
        if court:
            params['docket__court'] = court
            
        try:
            data = self._make_request('audio/', params)
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Error searching audio recordings: {str(e)}")
            return []

    def get_financial_disclosure(self, person_id: int) -> List[Dict]:
        """Get financial disclosure information for a judge"""
        params = {
            'person': person_id,
            'format': 'json'
        }
        
        try:
            data = self._make_request('financial-disclosures/', params)
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Error getting financial disclosure: {str(e)}")
            return []

    def search_attorneys(self, name: str, organization: str = None) -> List[AttorneyInfo]:
        """Search for attorneys by name and organization"""
        params = {
            'name': name,
            'format': 'json'
        }
        
        if organization:
            params['organizations'] = organization
        
        try:
            data = self._make_request('attorneys/', params)
            attorneys = []
            
            for attorney_data in data.get('results', []):
                attorney = AttorneyInfo(
                    id=attorney_data.get('id', 0),
                    name=attorney_data.get('name', ''),
                    bar_admissions=attorney_data.get('bar_admissions', []),
                    organizations=[org.get('name', '') for org in attorney_data.get('organizations', [])],
                    contact_info=attorney_data.get('contact_raw', {}),
                    case_count=0,  # Will be populated by separate call
                    specialties=[]  # Will be inferred from case history
                )
                attorneys.append(attorney)
            
            return attorneys
        except Exception as e:
            logger.error(f"Error searching attorneys: {str(e)}")
            return []
    
    def get_attorney_case_history(self, attorney_id: int, limit: int = 100) -> List[Dict]:
        """Get case history for a specific attorney"""
        params = {
            'attorney': attorney_id,
            'format': 'json',
            'page_size': limit,
            'ordering': '-date_created'
        }
        
        try:
            # Search in parties (attorney representations)
            data = self._make_request('parties/', params)
            cases = []
            
            for party_data in data.get('results', []):
                if 'docket' in party_data:
                    docket = party_data['docket']
                    case_info = {
                        'case_id': docket.get('id', ''),
                        'case_name': docket.get('case_name', ''),
                        'court': docket.get('court', {}).get('full_name', ''),
                        'date_filed': docket.get('date_filed', ''),
                        'case_type': docket.get('nature_of_suit', ''),
                        'party_type': party_data.get('party_type', ''),
                        'status': docket.get('docket_number', '')
                    }
                    cases.append(case_info)
            
            return cases
        except Exception as e:
            logger.error(f"Error getting attorney case history: {str(e)}")
            return []
    
    def analyze_law_firm(self, firm_name: str) -> LawFirmAnalysis:
        """Analyze a law firm's performance and track record"""
        try:
            # Search for attorneys at the firm
            attorneys = self.search_attorneys('', firm_name)
            
            # Get case history for the firm
            total_cases = 0
            practice_areas = set()
            recent_cases = []
            
            for attorney in attorneys[:5]:  # Analyze top 5 attorneys
                cases = self.get_attorney_case_history(attorney.id, 20)
                total_cases += len(cases)
                
                for case in cases:
                    if case.get('case_type'):
                        practice_areas.add(case['case_type'])
                    recent_cases.append(case)
            
            # Calculate success metrics (simplified)
            success_metrics = {
                'total_attorneys': len(attorneys),
                'total_cases': total_cases,
                'avg_cases_per_attorney': total_cases / len(attorneys) if attorneys else 0,
                'practice_areas_count': len(practice_areas)
            }
            
            return LawFirmAnalysis(
                attorneys=attorneys,
                total_cases=total_cases,
                practice_areas=list(practice_areas),
                success_metrics=success_metrics,
                recent_cases=recent_cases[:10]
            )
            
        except Exception as e:
            logger.error(f"Error analyzing law firm: {str(e)}")
            return LawFirmAnalysis(
                attorneys=[],
                total_cases=0,
                practice_areas=[],
                success_metrics={},
                recent_cases=[]
            )
    
    def get_judge_information(self, judge_name: str) -> Dict:
        """Get information about a judge"""
        params = {
            'name_full': judge_name,
            'format': 'json'
        }
        
        try:
            data = self._make_request('people/', params)
            judges = data.get('results', [])
            
            if judges:
                judge = judges[0]  # Take first match
                return {
                    'id': judge.get('id'),
                    'name': judge.get('name_full', ''),
                    'positions': judge.get('positions', []),
                    'education': judge.get('educations', []),
                    'political_affiliations': judge.get('political_affiliations', []),
                    'aba_ratings': judge.get('aba_ratings', []),
                    'appointed_by': judge.get('appointer', ''),
                    'confirmation_date': judge.get('date_confirmation')
                }
            
            return {}
        except Exception as e:
            logger.error(f"Error getting judge information: {str(e)}")
            return {}
    
    def search_similar_cases(self, case_description: str, court: str = None, limit: int = 10) -> List[Dict]:
        """Search for similar cases based on description"""
        params = {
            'q': case_description,
            'type': 'o',  # Opinions
            'format': 'json',
            'page_size': limit
        }
        
        if court:
            params['court'] = court
        
        try:
            data = self._make_request('search/', params)
            similar_cases = []
            
            for result in data.get('results', []):
                case_info = {
                    'case_name': result.get('caseName', ''),
                    'court': result.get('court', ''),
                    'date_filed': result.get('dateFiled', ''),
                    'citation': result.get('citation', []),
                    'snippet': result.get('snippet', ''),
                    'relevance_score': result.get('score', 0)
                }
                similar_cases.append(case_info)
            
            return similar_cases
        except Exception as e:
            logger.error(f"Error searching similar cases: {str(e)}")
            return []
    
    def _calculate_success_metrics(self, cases: List[Dict]) -> Dict[str, float]:
        """Calculate success metrics from case history"""
        if not cases:
            return {}
        
        # This is a simplified calculation
        # In reality, you'd need more detailed case outcome data
        metrics = {
            'total_cases': len(cases),
            'avg_cases_per_year': 0,
            'court_diversity': 0,
            'practice_area_diversity': 0
        }
        
        # Calculate cases per year
        if cases:
            date_range = self._get_date_range(cases)
            if date_range > 0:
                metrics['avg_cases_per_year'] = len(cases) / date_range
        
        # Calculate diversity metrics
        courts = set(case.get('court', '') for case in cases)
        practice_areas = set(case.get('case_type', '') for case in cases)
        
        metrics['court_diversity'] = len(courts)
        metrics['practice_area_diversity'] = len(practice_areas)
        
        return metrics
    
    def _get_date_range(self, cases: List[Dict]) -> float:
        """Get date range in years from cases"""
        dates = []
        for case in cases:
            if case.get('date_filed'):
                try:
                    date = datetime.strptime(case['date_filed'], '%Y-%m-%d')
                    dates.append(date)
                except:
                    continue
        
        if len(dates) < 2:
            return 1.0
        
        date_range = (max(dates) - min(dates)).days / 365.25
        return max(date_range, 1.0)

class LegalIntelligenceService:
    """Service for legal intelligence using CourtListener data"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.client = CourtListenerClient(api_token)
    
    def verify_attorney_credentials(self, attorney_name: str, law_firm: str = None) -> Dict:
        """Verify attorney credentials and get background information"""
        attorneys = self.client.search_attorneys(attorney_name, law_firm)
        
        if not attorneys:
            return {
                'verified': False,
                'message': 'Attorney not found in CourtListener database'
            }
        
        attorney = attorneys[0]  # Take first match
        case_history = self.client.get_attorney_case_history(attorney.id, 20)
        
        return {
            'verified': True,
            'attorney_info': {
                'name': attorney.name,
                'bar_admissions': attorney.bar_admissions,
                'organizations': attorney.organizations,
                'recent_case_count': len(case_history),
                'recent_cases': case_history[:5]  # Show 5 most recent
            }
        }
    
    def analyze_opposing_counsel(self, attorney_name: str, law_firm: str = None) -> Dict:
        """Analyze opposing counsel for strategic insights"""
        firm_profile = self.client.analyze_law_firm(law_firm) if law_firm else None
        attorney_verification = self.verify_attorney_credentials(attorney_name, law_firm)
        
        analysis = {
            'attorney_experience': attorney_verification,
            'strategic_insights': []
        }
        
        if firm_profile:
            analysis['firm_profile'] = {
                'name': firm_profile.name,
                'total_attorneys': len(firm_profile.attorneys),
                'total_cases': firm_profile.total_cases,
                'practice_areas': firm_profile.practice_areas,
                'courts_appeared': firm_profile.courts_appeared[:10],  # Top 10 courts
                'success_metrics': firm_profile.success_metrics
            }
            
            # Generate strategic insights
            if firm_profile.total_cases > 100:
                analysis['strategic_insights'].append(
                    "High-volume firm with extensive litigation experience"
                )
            
            if len(firm_profile.practice_areas) > 5:
                analysis['strategic_insights'].append(
                    "Diversified practice areas - may not be specialized in this area"
                )
            
            federal_courts = [court for court in firm_profile.courts_appeared 
                            if 'District' in court or 'Circuit' in court]
            if len(federal_courts) > 5:
                analysis['strategic_insights'].append(
                    "Extensive federal court experience"
                )
        
        return analysis
    
    def estimate_case_complexity(self, case_description: str, court: str = None) -> Dict:
        """Estimate case complexity based on similar cases"""
        similar_cases = self.client.search_similar_cases(case_description, court, 20)
        
        if not similar_cases:
            return {
                'complexity_score': 5,  # Medium complexity
                'confidence': 'Low',
                'reasoning': 'No similar cases found for comparison'
            }
        
        # Analyze similar cases for complexity indicators
        complexity_indicators = {
            'high_court_level': 0,
            'long_duration': 0,
            'multiple_parties': 0,
            'complex_legal_issues': 0
        }
        
        for case in similar_cases:
            # High court level (appellate courts = more complex)
            if any(indicator in case.get('court', '').lower() 
                   for indicator in ['supreme', 'circuit', 'appellate']):
                complexity_indicators['high_court_level'] += 1
            
            # Complex legal issues (based on snippet content)
            snippet = case.get('snippet', '').lower()
            if any(indicator in snippet 
                   for indicator in ['constitutional', 'precedent', 'novel', 'first impression']):
                complexity_indicators['complex_legal_issues'] += 1
        
        # Calculate complexity score (1-10)
        total_indicators = sum(complexity_indicators.values())
        max_possible = len(similar_cases) * len(complexity_indicators)
        
        if max_possible > 0:
            complexity_ratio = total_indicators / max_possible
            complexity_score = min(10, max(1, int(complexity_ratio * 10)))
        else:
            complexity_score = 5
        
        confidence = 'High' if len(similar_cases) >= 10 else 'Medium' if len(similar_cases) >= 5 else 'Low'
        
        return {
            'complexity_score': complexity_score,
            'confidence': confidence,
            'similar_cases_found': len(similar_cases),
            'complexity_indicators': complexity_indicators,
            'reasoning': self._generate_complexity_reasoning(complexity_score, complexity_indicators)
        }
    
    def get_judge_insights(self, judge_name: str) -> Dict:
        """Get insights about a judge for case strategy"""
        judge_info = self.client.get_judge_information(judge_name)
        
        if not judge_info:
            return {
                'found': False,
                'message': 'Judge information not available'
            }
        
        insights = {
            'found': True,
            'judge_info': judge_info,
            'strategic_insights': []
        }
        
        # Generate insights based on judge information
        positions = judge_info.get('positions', [])
        for position in positions:
            if position.get('position_type') == 'jud':
                tenure_years = self._calculate_tenure(position.get('date_start'))
                if tenure_years > 10:
                    insights['strategic_insights'].append(
                        f"Experienced judge with {tenure_years} years on the bench"
                    )
        
        # Educational background insights
        education = judge_info.get('education', [])
        if education:
            law_schools = [edu.get('school', {}).get('name', '') for edu in education]
            if any('Harvard' in school or 'Yale' in school or 'Stanford' in school 
                   for school in law_schools):
                insights['strategic_insights'].append(
                    "Judge attended prestigious law school"
                )
        
        return insights
    
    def comprehensive_case_research(self, case_description: str, court: str = None) -> Dict:
        """Comprehensive case research using multiple CourtListener endpoints"""
        try:
            research_results = {
                'case_description': case_description,
                'court': court,
                'research_timestamp': datetime.now(timezone.utc).isoformat(),
                'findings': {}
            }
            
            # Search for similar dockets/cases
            similar_dockets = self.client.search_dockets(
                case_name=case_description[:100],  # Truncate for search
                court=court,
                limit=10
            )
            
            research_results['findings']['similar_cases'] = []
            for docket in similar_dockets:
                case_info = {
                    'case_name': docket.case_name,
                    'docket_number': docket.docket_number,
                    'court': docket.court,
                    'date_filed': docket.date_filed,
                    'date_terminated': docket.date_terminated,
                    'nature_of_suit': docket.nature_of_suit,
                    'status': 'Terminated' if docket.date_terminated else 'Active'
                }
                
                # Get docket entries for the first few cases
                if len(research_results['findings']['similar_cases']) < 3:
                    entries = self.client.get_docket_entries(docket.id, limit=10)
                    case_info['recent_filings'] = [
                        {
                            'date': entry.get('date_filed'),
                            'description': entry.get('description', '')[:200]
                        }
                        for entry in entries[:5]
                    ]
                
                research_results['findings']['similar_cases'].append(case_info)
            
            # Search for relevant opinions
            opinions = self.client.search_opinions(
                query=case_description[:200],
                court=court,
                limit=10
            )
            
            research_results['findings']['relevant_opinions'] = []
            for opinion in opinions:
                opinion_info = {
                    'case_name': opinion.get('case_name', ''),
                    'date_filed': opinion.get('date_filed'),
                    'court': opinion.get('court', {}).get('full_name', ''),
                    'author': opinion.get('author_str', ''),
                    'type': opinion.get('type', ''),
                    'snippet': opinion.get('snippet', '')[:300]
                }
                research_results['findings']['relevant_opinions'].append(opinion_info)
            
            # Generate research summary
            research_results['summary'] = self._generate_research_summary(
                len(similar_dockets), len(opinions)
            )
            
            return research_results
            
        except Exception as e:
            logger.error(f"Error in comprehensive case research: {str(e)}")
            return {
                'error': f'Research failed: {str(e)}',
                'case_description': case_description
            }

    def analyze_judge_patterns(self, judge_name: str) -> Dict:
        """Analyze patterns in a judge's decisions and case management"""
        try:
            judge_info = self.client.get_judge_information(judge_name)
            
            if not judge_info:
                return {
                    'found': False,
                    'message': 'Judge information not available'
                }
            
            analysis = {
                'judge_info': judge_info,
                'case_patterns': {},
                'decision_trends': {},
                'strategic_insights': []
            }
            
            # Search for cases where this judge presided
            if judge_info.get('id'):
                # Get financial disclosures if available
                disclosures = self.client.get_financial_disclosure(judge_info['id'])
                if disclosures:
                    analysis['financial_disclosures'] = len(disclosures)
                    analysis['strategic_insights'].append(
                        f"Judge has {len(disclosures)} financial disclosure(s) on file"
                    )
            
            # Analyze tenure and experience
            positions = judge_info.get('positions', [])
            judicial_positions = [pos for pos in positions if pos.get('position_type') == 'jud']
            
            if judicial_positions:
                current_position = judicial_positions[0]
                tenure_years = self._calculate_tenure(current_position.get('date_start'))
                analysis['case_patterns']['tenure_years'] = tenure_years
                
                if tenure_years > 15:
                    analysis['strategic_insights'].append(
                        "Highly experienced judge with extensive tenure"
                    )
                elif tenure_years > 5:
                    analysis['strategic_insights'].append(
                        "Experienced judge with solid track record"
                    )
                else:
                    analysis['strategic_insights'].append(
                        "Relatively new to the bench - limited historical data"
                    )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing judge patterns: {str(e)}")
            return {'error': f'Analysis failed: {str(e)}'}

    def competitive_firm_analysis(self, firm_names: List[str], practice_area: str = None) -> Dict:
        """Compare multiple law firms using CourtListener data"""
        try:
            comparison_results = {
                'practice_area': practice_area,
                'firms_analyzed': len(firm_names),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'firm_profiles': {},
                'comparative_metrics': {}
            }
            
            all_firm_data = []
            
            for firm_name in firm_names:
                firm_profile = self.client.analyze_law_firm(firm_name)
                
                firm_data = {
                    'name': firm_name,
                    'total_attorneys': len(firm_profile.attorneys),
                    'total_cases': firm_profile.total_cases,
                    'practice_areas': firm_profile.practice_areas,
                    'courts_appeared': firm_profile.courts_appeared,
                    'success_metrics': firm_profile.success_metrics,
                    'recent_case_volume': len(firm_profile.recent_cases)
                }
                
                # Practice area specialization score
                if practice_area and practice_area in firm_profile.practice_areas:
                    # Simple specialization score based on practice area frequency
                    specialization_score = min(10, firm_profile.practice_areas.count(practice_area) * 2)
                    firm_data['specialization_score'] = specialization_score
                else:
                    firm_data['specialization_score'] = 0
                
                comparison_results['firm_profiles'][firm_name] = firm_data
                all_firm_data.append(firm_data)
            
            # Generate comparative metrics
            if all_firm_data:
                comparison_results['comparative_metrics'] = {
                    'highest_case_volume': max(all_firm_data, key=lambda x: x['total_cases'])['name'],
                    'most_attorneys': max(all_firm_data, key=lambda x: x['total_attorneys'])['name'],
                    'most_specialized': max(all_firm_data, key=lambda x: x['specialization_score'])['name'] if practice_area else None,
                    'average_case_volume': sum(f['total_cases'] for f in all_firm_data) / len(all_firm_data),
                    'average_attorney_count': sum(f['total_attorneys'] for f in all_firm_data) / len(all_firm_data)
                }
            
            return comparison_results
            
        except Exception as e:
            logger.error(f"Error in competitive firm analysis: {str(e)}")
            return {'error': f'Analysis failed: {str(e)}'}

    def legal_precedent_research(self, legal_issue: str, jurisdiction: str = None) -> Dict:
        """Research legal precedents for a specific issue"""
        try:
            research_results = {
                'legal_issue': legal_issue,
                'jurisdiction': jurisdiction,
                'research_timestamp': datetime.now(timezone.utc).isoformat(),
                'precedents': [],
                'citation_network': {}
            }
            
            # Search for relevant opinions
            opinions = self.client.search_opinions(
                query=legal_issue,
                court=jurisdiction,
                limit=15
            )
            
            precedent_cases = []
            
            for opinion in opinions[:10]:  # Analyze top 10 opinions
                precedent = {
                    'case_name': opinion.get('case_name', ''),
                    'court': opinion.get('court', {}).get('full_name', ''),
                    'date_filed': opinion.get('date_filed'),
                    'author': opinion.get('author_str', ''),
                    'opinion_type': opinion.get('type', ''),
                    'relevance_snippet': opinion.get('snippet', '')[:500],
                    'citations': {
                        'cited_by': [],
                        'cites': []
                    }
                }
                
                # Get citation network for important cases
                if opinion.get('id'):
                    citing_cases = self.client.search_citing_cases(opinion['id'])
                    cited_cases = self.client.search_cited_cases(opinion['id'])
                    
                    precedent['citations']['cited_by'] = [
                        {
                            'case_name': case.get('citing_opinion', {}).get('case_name', ''),
                            'court': case.get('citing_opinion', {}).get('court', '')
                        }
                        for case in citing_cases[:5]
                    ]
                    
                    precedent['citations']['cites'] = [
                        {
                            'case_name': case.get('cited_opinion', {}).get('case_name', ''),
                            'court': case.get('cited_opinion', {}).get('court', '')
                        }
                        for case in cited_cases[:5]
                    ]
                    
                    # Calculate precedential value
                    precedent['precedential_value'] = len(citing_cases)
                
                precedent_cases.append(precedent)
            
            research_results['precedents'] = precedent_cases
            
            # Generate research insights
            research_results['insights'] = self._generate_precedent_insights(precedent_cases)
            
            return research_results
            
        except Exception as e:
            logger.error(f"Error in legal precedent research: {str(e)}")
            return {'error': f'Research failed: {str(e)}'}

    def court_analytics(self, court_identifier: str) -> Dict:
        """Analyze court statistics and patterns"""
        try:
            # Get court information
            court_info = self.client.get_court_info(court_identifier)
            
            if not court_info:
                return {
                    'found': False,
                    'message': 'Court information not available'
                }
            
            analytics = {
                'court_info': court_info,
                'case_statistics': {},
                'timing_patterns': {},
                'strategic_insights': []
            }
            
            # Search for recent dockets in this court
            recent_dockets = self.client.search_dockets(
                court=court_identifier,
                date_filed_after=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                limit=100
            )
            
            if recent_dockets:
                # Calculate case statistics
                total_cases = len(recent_dockets)
                terminated_cases = len([d for d in recent_dockets if d.date_terminated])
                active_cases = total_cases - terminated_cases
                
                analytics['case_statistics'] = {
                    'total_recent_cases': total_cases,
                    'active_cases': active_cases,
                    'terminated_cases': terminated_cases,
                    'termination_rate': terminated_cases / total_cases if total_cases > 0 else 0
                }
                
                # Analyze case types
                case_types = {}
                for docket in recent_dockets:
                    case_type = docket.nature_of_suit or 'Unknown'
                    case_types[case_type] = case_types.get(case_type, 0) + 1
                
                analytics['case_statistics']['common_case_types'] = sorted(
                    case_types.items(), key=lambda x: x[1], reverse=True
                )[:10]
                
                # Generate insights
                if analytics['case_statistics']['termination_rate'] > 0.7:
                    analytics['strategic_insights'].append(
                        "High case termination rate - court moves cases efficiently"
                    )
                elif analytics['case_statistics']['termination_rate'] < 0.3:
                    analytics['strategic_insights'].append(
                        "Low case termination rate - expect longer case duration"
                    )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error in court analytics: {str(e)}")
            return {'error': f'Analysis failed: {str(e)}'}

    def _generate_research_summary(self, similar_cases_count: int, opinions_count: int) -> str:
        """Generate a summary of research findings"""
        if similar_cases_count == 0 and opinions_count == 0:
            return "Limited precedent data available - may indicate novel legal issue"
        elif similar_cases_count > 10 or opinions_count > 10:
            return "Extensive precedent data available - well-established area of law"
        else:
            return "Moderate precedent data available - some guidance from prior cases"

    def _generate_precedent_insights(self, precedents: List[Dict]) -> List[str]:
        """Generate insights from precedent analysis"""
        insights = []
        
        if not precedents:
            insights.append("No relevant precedents found")
            return insights
        
        # Analyze citation patterns
        highly_cited = [p for p in precedents if p.get('precedential_value', 0) > 10]
        if highly_cited:
            insights.append(f"Found {len(highly_cited)} highly cited precedent(s)")
        
        # Analyze court levels
        supreme_court_cases = [p for p in precedents if 'Supreme' in p.get('court', '')]
        if supreme_court_cases:
            insights.append(f"Includes {len(supreme_court_cases)} Supreme Court precedent(s)")
        
        # Analyze recency
        recent_cases = [p for p in precedents 
                       if p.get('date_filed') and 
                       datetime.strptime(p['date_filed'], '%Y-%m-%d') > datetime.now() - timedelta(days=1825)]  # 5 years
        if recent_cases:
            insights.append(f"{len(recent_cases)} recent precedents (within 5 years)")
        
        return insights

    # ... existing methods remain the same ...
