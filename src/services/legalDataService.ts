/**
 * Legal Data Service
 * 
 * Integrates multiple legal data sources including:
 * - CourtListener API for case law, court records, and judicial data
 * - LAIT Backend API for legal intelligence features
 * - Legal document analysis
 * - Citation lookup and verification
 */

import axios, { AxiosResponse } from 'axios';

// API Configuration
const COURTLISTENER_API_BASE = 'https://www.courtlistener.com/api/rest/v4';
const COURTLISTENER_SEARCH_API = 'https://www.courtlistener.com/api/rest/v4/search';
const LAIT_BACKEND_API = 'http://127.0.0.1:5003/api'; // Enhanced backend API

// CourtListener API Configuration
const COURTLISTENER_API = {
  BASE: 'https://www.courtlistener.com/api/rest/v4',
  SEARCH: 'https://www.courtlistener.com/api/rest/v4/search',
};

// Legal data types and interfaces
export interface Court {
  id: string;
  full_name: string;
  short_name: string;
  jurisdiction: string;
  date_created: string;
  position: number;
  has_opinion_scraper: boolean;
  has_oral_argument_scraper: boolean;
  start_date?: string;
  end_date?: string;
  citation_string: string;
}

export interface Opinion {
  id: number;
  resource_uri: string;
  absolute_url: string;
  cluster: string;
  author: any;
  joined_by: any[];
  type: string;
  sha1: string;
  page_count?: number;
  download_url?: string;
  local_path?: string;
  plain_text: string;
  html: string;
  html_lawbox?: string;
  html_columbia?: string;
  html_anon_2020?: string;
  xml_harvard?: string;
  html_with_citations: string;
  extracted_by_ocr: boolean;
  date_created: string;
  date_modified: string;
}

export interface OpinionCluster {
  id: number;
  resource_uri: string;
  absolute_url: string;
  panel: any[];
  panel_ids: number[];
  panel_names: string[];
  non_participating_judges: any[];
  non_participating_judge_ids: number[];
  judges: string;
  date_created: string;
  date_modified: string;
  date_filed: string;
  date_filed_is_approximate: boolean;
  slug: string;
  citation_id: number;
  citation_count: number;
  precedential_status: string;
  date_blocked?: string;
  blocked: boolean;
  syllabus: string;
  headnotes: string;
  summary: string;
  disposition: string;
  history: string;
  other_dates: string;
  cross_reference: string;
  correction: string;
  citation_string: string;
  precedential_status_string: string;
  date_filed_formatted: string;
  docket: string;
  sub_opinions: Opinion[];
  source: string;
  procedural_history: string;
  attorneys: string;
  nature_of_suit: string;
  posture: string;
  scdb_id?: string;
  scdb_decision_direction?: number;
  scdb_votes_majority?: number;
  scdb_votes_minority?: number;
}

export interface Docket {
  id: number;
  resource_uri: string;
  absolute_url: string;
  court: string;
  clusters: OpinionCluster[];
  audio_files: any[];
  assigned_to?: any;
  assigned_to_str: string;
  referred_to?: any;
  referred_to_str: string;
  date_created: string;
  date_modified: string;
  date_cert_granted?: string;
  date_cert_denied?: string;
  date_argued?: string;
  date_reargued?: string;
  date_reargument_denied?: string;
  date_filed?: string;
  date_terminated?: string;
  date_last_filing?: string;
  case_name_short: string;
  case_name: string;
  case_name_full: string;
  slug: string;
  docket_number: string;
  docket_number_core: string;
  pacer_case_id?: string;
  cause: string;
  nature_of_suit: string;
  jury_demand: string;
  jurisdiction_type: string;
  appellate_fee_status: string;
  appellate_case_type_information: string;
  mdl_status: string;
  filepath_local?: string;
  filepath_ia?: string;
  filepath_ia_json?: string;
  ia_upload_failure_count?: number;
  ia_needs_upload?: boolean;
  ia_date_first_change?: string;
  view_count: number;
  date_blocked?: string;
  blocked: boolean;
  appeal_from?: any;
  appeal_from_str: string;
  panel_str: string;
  originating_court_information?: any;
  idb_data?: any;
}

export interface Judge {
  id: number;
  resource_uri: string;
  absolute_url: string;
  name_first: string;
  name_middle: string;
  name_last: string;
  name_suffix: string;
  date_created: string;
  date_modified: string;
  date_completed: string;
  fjc_id?: number;
  slug: string;
  gender: string;
  religion: string;
  ftm_total_received?: number;
  ftm_eid: string;
  has_photo: boolean;
  name_full: string;
  date_granularity_birth: string;
  date_birth?: string;
  place_birth_city: string;
  place_birth_state: string;
  date_granularity_death: string;
  date_death?: string;
  place_death_city: string;
  place_death_state: string;
  positions: any[];
  educations: any[];
  political_affiliations: any[];
  aba_ratings: any[];
  sources: any[];
}

export interface SearchParams {
  q?: string;
  court?: string;
  judge?: string;
  case_name?: string;
  docket_number?: string;
  citation?: string;
  neutral_cite?: string;
  filed_after?: string;
  filed_before?: string;
  order_by?: string;
  type?: 'o' | 'r' | 'p' | 'oa'; // opinions, recap, people, oral arguments
  stat_Precedential?: boolean;
  stat_Non_Precedential?: boolean;
  stat_Errata?: boolean;
  stat_Separate?: boolean;
  stat_In_chambers?: boolean;
  stat_Relating_to_orders?: boolean;
  stat_Unknown?: boolean;
}

export interface SearchResult {
  count: number;
  next?: string;
  previous?: string;
  results: any[];
}

export interface LegalAnalytics {
  totalCases: number;
  recentTrends: {
    period: string;
    caseCount: number;
    avgDuration: number;
  }[];
  topCourts: {
    court: string;
    caseCount: number;
    percentage: number;
  }[];
  caseTypeDistribution: {
    type: string;
    count: number;
    percentage: number;
  }[];
  citationNetwork: {
    mostCited: Opinion[];
    citationTrends: any[];
  };
}

export interface VendorRiskProfile {
  vendorName: string;
  riskScore: number;
  legalExposure: {
    activeLitigation: number;
    pastSettlements: number;
    regulatoryActions: number;
  };
  practiceAreas: string[];
  jurisdictions: string[];
  averageCase: {
    duration: number;
    cost: number;
    successRate: number;
  };
}

class LegalDataService {
  private apiKey?: string;

  constructor(apiKey?: string) {
    this.apiKey = apiKey;
  }

  /**
   * Set API key for authenticated requests
   */
  setApiKey(apiKey: string): void {
    this.apiKey = apiKey;
  }

  /**
   * Get request headers with authentication if available
   */
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Token ${this.apiKey}`;
    }

    return headers;
  }

  /**
   * Search for legal opinions and cases
   */
  async searchOpinions(params: SearchParams): Promise<SearchResult> {
    try {
      // Validate and format dates
      if (params.filed_after) {
        const afterDate = new Date(params.filed_after);
        params.filed_after = afterDate.toISOString().split('T')[0];
      }
      if (params.filed_before) {
        const beforeDate = new Date(params.filed_before);
        params.filed_before = beforeDate.toISOString().split('T')[0];
      }

      // Add required query parameter if not present
      if (!params.q) {
        params.q = '*';  // Match all if no specific query
      }

      const response: AxiosResponse<SearchResult> = await axios.get(
        `${COURTLISTENER_SEARCH_API}/`,
        {
          params: { 
            ...params,
            type: 'o',
            format: 'json',
            page_size: 20
          },
          headers: {
            ...this.getHeaders(),
            'Accept': 'application/json'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error searching opinions:', error);
      throw new Error('Failed to search legal opinions');
    }
  }

  /**
   * Search PACER/RECAP data
   */
  async searchRecapData(params: SearchParams): Promise<SearchResult> {
    try {
      const response: AxiosResponse<SearchResult> = await axios.get(
        `${COURTLISTENER_SEARCH_API}/`,
        {
          params: { ...params, type: 'r' },
          headers: this.getHeaders(),
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error searching RECAP data:', error);
      throw new Error('Failed to search PACER data');
    }
  }

  /**
   * Search for judges and judicial information
   */
  async searchJudges(params: SearchParams): Promise<SearchResult> {
    try {
      const response: AxiosResponse<SearchResult> = await axios.get(
        `${COURTLISTENER_SEARCH_API}/`,
        {
          params: { ...params, type: 'p' },
          headers: this.getHeaders(),
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error searching judges:', error);
      throw new Error('Failed to search judicial data');
    }
  }

  /**
   * Get court information
   */
  async getCourts(): Promise<Court[]> {
    try {
      const response: AxiosResponse<{ results: Court[] }> = await axios.get(
        `${COURTLISTENER_API_BASE}/courts/`,
        {
          headers: this.getHeaders(),
        }
      );
      return response.data.results;
    } catch (error) {
      console.error('Error fetching courts:', error);
      throw new Error('Failed to fetch court information');
    }
  }

  /**
   * Get specific court by ID
   */
  async getCourt(courtId: string): Promise<Court> {
    try {
      const response: AxiosResponse<Court> = await axios.get(
        `${COURTLISTENER_API_BASE}/courts/${courtId}/`,
        {
          headers: this.getHeaders(),
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching court:', error);
      throw new Error('Failed to fetch court information');
    }
  }

  /**
   * Get opinion cluster by ID
   */
  async getOpinionCluster(clusterId: number): Promise<OpinionCluster> {
    try {
      const response: AxiosResponse<OpinionCluster> = await axios.get(
        `${COURTLISTENER_API_BASE}/clusters/${clusterId}/`,
        {
          headers: this.getHeaders(),
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching opinion cluster:', error);
      throw new Error('Failed to fetch opinion cluster');
    }
  }

  /**
   * Get opinion by ID
   */
  async getOpinion(opinionId: number): Promise<Opinion> {
    try {
      const response: AxiosResponse<Opinion> = await axios.get(
        `${COURTLISTENER_API_BASE}/opinions/${opinionId}/`,
        {
          headers: this.getHeaders(),
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching opinion:', error);
      throw new Error('Failed to fetch opinion');
    }
  }

  /**
   * Get docket by ID
   */
  async getDocket(docketId: number): Promise<Docket> {
    try {
      const response: AxiosResponse<Docket> = await axios.get(
        `${COURTLISTENER_API_BASE}/dockets/${docketId}/`,
        {
          headers: this.getHeaders(),
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching docket:', error);
      throw new Error('Failed to fetch docket');
    }
  }

  /**
   * Get judge by ID
   */
  async getJudge(judgeId: number): Promise<Judge> {
    try {
      const response: AxiosResponse<Judge> = await axios.get(
        `${COURTLISTENER_API_BASE}/people/${judgeId}/`,
        {
          headers: this.getHeaders(),
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching judge:', error);
      throw new Error('Failed to fetch judge information');
    }
  }

  /**
   * Lookup citation and verify its validity
   */
  async lookupCitation(citation: string): Promise<any> {
    try {
      const response = await axios.get(
        `${COURTLISTENER_API_BASE}/citation-lookup/`,
        {
          params: { citation },
          headers: this.getHeaders(),
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error looking up citation:', error);
      throw new Error('Failed to lookup citation');
    }
  }

  /**
   * Get legal analytics for a specific area or jurisdiction
   */
  async getLegalAnalytics(params: {
    jurisdiction?: string;
    practiceArea?: string;
    timeframe?: string;
  }): Promise<LegalAnalytics> {
    try {
      // Search for recent cases in the specified parameters
      const searchParams: SearchParams = {
        court: params.jurisdiction,
        filed_after: this.getDateRange(params.timeframe || '1y').start,
        filed_before: this.getDateRange(params.timeframe || '1y').end,
        order_by: '-date_filed',
      };

      if (params.practiceArea) {
        searchParams.q = params.practiceArea;
      }

      let searchResult;
      try {
        searchResult = await this.searchOpinions(searchParams);
      } catch (error) {
        console.warn('Failed to fetch live data, using fallback data', error);
        // Use fallback data
        searchResult = {
          count: 0,
          results: []
        };
      }
      
      // Process results to generate analytics with fallback data
      const analytics: LegalAnalytics = {
        totalCases: searchResult.count || 0,
        recentTrends: await this.calculateTrends(searchParams).catch(() => []),
        topCourts: await this.getTopCourts(searchParams).catch(() => []),
        caseTypeDistribution: await this.getCaseTypeDistribution(searchParams).catch(() => []),
        citationNetwork: await this.getCitationNetwork(searchParams),
      };

      return analytics;
    } catch (error) {
      console.error('Error generating legal analytics:', error);
      throw new Error('Failed to generate legal analytics');
    }
  }

  /**
   * Analyze vendor legal risk profile
   */
  async analyzeVendorRisk(vendorName: string): Promise<VendorRiskProfile> {
    try {
      // Search for cases involving the vendor
      const searchResults = await this.searchOpinions({
        q: `"${vendorName}"`,
        order_by: '-date_filed',
      });

      const recapResults = await this.searchRecapData({
        q: `"${vendorName}"`,
        order_by: '-date_filed',
      });

      // Process results to calculate risk profile
      const riskProfile: VendorRiskProfile = {
        vendorName,
        riskScore: this.calculateRiskScore(searchResults, recapResults),
        legalExposure: {
          activeLitigation: recapResults.count,
          pastSettlements: this.countSettlements(searchResults),
          regulatoryActions: this.countRegulatoryActions(searchResults),
        },
        practiceAreas: this.extractPracticeAreas(searchResults),
        jurisdictions: this.extractJurisdictions(searchResults),
        averageCase: this.calculateAverageCase(searchResults),
      };

      return riskProfile;
    } catch (error) {
      console.error('Error analyzing vendor risk:', error);
      throw new Error('Failed to analyze vendor legal risk');
    }
  }

  /**
   * Helper methods
   */
  private getDateRange(timeframe: string): { start: string; end: string } {
    const end = new Date();
    const start = new Date();

    switch (timeframe) {
      case '1m':
        start.setMonth(start.getMonth() - 1);
        break;
      case '3m':
        start.setMonth(start.getMonth() - 3);
        break;
      case '6m':
        start.setMonth(start.getMonth() - 6);
        break;
      case '1y':
      default:
        start.setFullYear(start.getFullYear() - 1);
        break;
    }

    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0],
    };
  }

  private async calculateTrends(params: SearchParams): Promise<any[]> {
    // Implementation for trend calculation
    return [];
  }

  private async getTopCourts(params: SearchParams): Promise<any[]> {
    // Implementation for top courts analysis
    return [];
  }

  private async getCaseTypeDistribution(params: SearchParams): Promise<any[]> {
    // Implementation for case type distribution
    return [];
  }

  private async getCitationNetwork(params: SearchParams): Promise<any> {
    // Implementation for citation network analysis
    return { mostCited: [], citationTrends: [] };
  }

  private calculateRiskScore(opinions: SearchResult, recap: SearchResult): number {
    // Implementation for risk score calculation
    const base = Math.min(100, (opinions.count + recap.count) * 2);
    return Math.max(0, Math.min(100, base));
  }

  private countSettlements(searchResults: SearchResult): number {
    // Implementation for counting settlements
    return 0;
  }

  private countRegulatoryActions(searchResults: SearchResult): number {
    // Implementation for counting regulatory actions
    return 0;
  }

  private extractPracticeAreas(searchResults: SearchResult): string[] {
    // Implementation for extracting practice areas
    return [];
  }

  private extractJurisdictions(searchResults: SearchResult): string[] {
    // Implementation for extracting jurisdictions
    return [];
  }

  private calculateAverageCase(searchResults: SearchResult): any {
    // Implementation for calculating average case metrics
    return { duration: 0, cost: 0, successRate: 0 };
  }

  // LAIT Backend API Methods
  
  /**
   * Test connection to LAIT backend
   */
  async testBackendConnection(): Promise<any> {
    try {
      const response = await axios.get(`${LAIT_BACKEND_API}/health`);
      return response.data;
    } catch (error) {
      console.error('Failed to connect to LAIT backend:', error);
      throw error;
    }
  }

  /**
   * Get legal intelligence test data
   */
  async getLegalIntelligenceTest(): Promise<any> {
    try {
      const response = await axios.get(`${LAIT_BACKEND_API}/legal-intelligence/test`);
      return response.data;
    } catch (error) {
      console.error('Failed to get legal intelligence test data:', error);
      throw error;
    }
  }

  /**
   * Search legal cases using LAIT backend (when available)
   */
  async searchCasesBackend(query: string, options?: any): Promise<any> {
    try {
      // When backend routes are fully implemented, this will call:
      // const response = await axios.post(`${LAIT_BACKEND_API}/legal-intelligence/search-cases`, {
      //   query,
      //   ...options
      // });
      
      // For now, return mock data with structure similar to expected response
      return {
        cases: [
          {
            id: '1',
            title: `${query} - Contract Dispute Analysis`,
            court: 'District Court of California',
            date: '2024-01-15',
            relevance: 95,
            excerpt: `Legal analysis shows precedent for ${query} related cases...`,
            source: 'lait-backend'
          },
          {
            id: '2',
            title: `${query} - Regulatory Compliance Case`,
            court: 'Federal Circuit Court',
            date: '2023-11-20',
            relevance: 87,
            excerpt: `Court ruling establishes framework for ${query} compliance...`,
            source: 'lait-backend'
          }
        ],
        total: 2,
        query: query
      };
    } catch (error) {
      console.error('Failed to search cases via backend:', error);
      throw error;
    }
  }

  /**
   * Get vendor risk assessment (mock implementation)
   */
  async getVendorRiskAssessment(vendorName?: string): Promise<any> {
    try {
      // When backend routes are fully implemented, this will call:
      // const response = await axios.post(`${LAIT_BACKEND_API}/legal-intelligence/vendor-risk-assessment`, {
      //   vendor_name: vendorName
      // });
      
      // For now, return mock data
      return {
        assessments: [
          {
            vendor: vendorName || 'TechCorp Solutions',
            riskLevel: 'high',
            score: 85,
            factors: ['Multiple ongoing litigations', 'Financial instability indicators', 'Regulatory violations'],
            lastUpdated: new Date().toISOString()
          },
          {
            vendor: 'SecureData Inc.',
            riskLevel: 'low',
            score: 25,
            factors: ['Clean legal record', 'Strong compliance history', 'Financial stability'],
            lastUpdated: new Date().toISOString()
          }
        ]
      };
    } catch (error) {
      console.error('Failed to get vendor risk assessment:', error);
      throw error;
    }
  }

  /**
   * Get legal analytics data from LAIT backend
   */
  async getLegalAnalyticsBackend(): Promise<any> {
    try {
      // When backend routes are fully implemented, this will call:
      // const response = await axios.get(`${LAIT_BACKEND_API}/legal-intelligence/analytics`);
      
      // For now, return mock analytics data
      return {
        totalCases: 15847,
        favorableOutcomes: 78,
        activeAttorneys: 342,
        trends: [
          { category: 'Contract Disputes', change: 15, direction: 'up' },
          { category: 'Intellectual Property', change: -8, direction: 'down' },
          { category: 'Employment Law', change: 23, direction: 'up' },
          { category: 'Regulatory Compliance', change: -12, direction: 'down' }
        ],
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      console.error('Failed to get legal analytics:', error);
      throw error;
    }
  }

  /**
   * Verify attorney credentials (mock implementation)
   */
  async verifyAttorney(attorneyName: string, barNumber?: string): Promise<any> {
    try {
      // When backend routes are fully implemented, this will call:
      // const response = await axios.post(`${LAIT_BACKEND_API}/legal-intelligence/verify-attorney`, {
      //   attorney_name: attorneyName,
      //   bar_number: barNumber
      // });
      
      // For now, return mock verification data
      return {
        verified: true,
        attorney: {
          name: attorneyName,
          barNumber: barNumber || 'CA123456',
          state: 'California',
          admissionDate: '2015-06-15',
          status: 'Active',
          disciplinaryRecord: 'Clean',
          practiceAreas: ['Corporate Law', 'Contract Disputes', 'Intellectual Property']
        },
        verificationDate: new Date().toISOString()
      };
    } catch (error) {
      console.error('Failed to verify attorney:', error);
      throw error;
    }
  }
}

export default LegalDataService;
