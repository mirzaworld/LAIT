import React, { useState } from 'react';
import { Search, Scale, Users, TrendingUp, AlertTriangle, FileText, Shield, BarChart3, File } from 'lucide-react';
import LegalDataService from '../services/legalDataService';
import DocumentAnalyzer from '../components/DocumentAnalyzer';

interface SearchResult {
  id: string;
  title: string;
  court: string;
  date: string;
  relevance: number;
  excerpt: string;
}

interface CaseDetails {
  id: string;
  title: string;
  court: string;
  date_filed: string;
  full_text: string;
  summary: string;
  citation: string;
  status: string;
  judges: string[];
  source: string;
  url?: string;
}

interface RiskAssessment {
  vendor: string;
  riskLevel: 'low' | 'medium' | 'high';
  score: number;
  factors: string[];
}

const LegalIntelligence: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'search' | 'analytics' | 'risk' | 'attorney' | 'documents'>('search');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [riskAssessments, setRiskAssessments] = useState<RiskAssessment[]>([]);
  const [attorneyName, setAttorneyName] = useState('');
  const [attorneyVerification, setAttorneyVerification] = useState<any>(null);
  const [selectedCase, setSelectedCase] = useState<CaseDetails | null>(null);
  const [showCaseDetails, setShowCaseDetails] = useState(false);

  // Initialize legal data service
  const legalService = new LegalDataService();

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      // Test backend connection first
      await legalService.testBackendConnection();
      
      // Use backend API for search
      const results = await legalService.searchCasesBackend(searchQuery);
      setSearchResults(results.cases || []);
    } catch (error) {
      console.error('Search failed:', error);
      // Fallback to mock data if backend is not available
      const mockResults: SearchResult[] = [
        {
          id: '1',
          title: `${searchQuery} - Contract Dispute`,
          court: 'District Court of California',
          date: '2024-01-15',
          relevance: 95,
          excerpt: 'Court ruled on vendor liability in service agreements...'
        },
        {
          id: '2',
          title: `${searchQuery} - Legal Precedent`,
          court: 'Federal Circuit Court',
          date: '2023-11-20',
          relevance: 87,
          excerpt: 'Precedent case involving government contractor obligations...'
        }
      ];
      setSearchResults(mockResults);
    } finally {
      setLoading(false);
    }
  };

  const loadRiskAssessments = async () => {
    try {
      const riskData = await legalService.getVendorRiskAssessment();
      setRiskAssessments(riskData.assessments || []);
    } catch (error) {
      console.error('Failed to load risk assessments:', error);
      // Fallback to mock data
      const mockRiskAssessments: RiskAssessment[] = [
        {
          vendor: 'TechCorp Solutions',
          riskLevel: 'high',
          score: 85,
          factors: ['Multiple ongoing litigations', 'Financial instability indicators', 'Regulatory violations']
        },
        {
          vendor: 'SecureData Inc.',
          riskLevel: 'low',
          score: 25,
          factors: ['Clean legal record', 'Strong compliance history', 'Financial stability']
        }
      ];
      setRiskAssessments(mockRiskAssessments);
    }
  };

  const handleAttorneyVerification = async () => {
    if (!attorneyName.trim()) return;
    
    setLoading(true);
    try {
      const verification = await legalService.verifyAttorney(attorneyName);
      setAttorneyVerification(verification);
    } catch (error) {
      console.error('Attorney verification failed:', error);
      setAttorneyVerification({
        verified: false,
        error: 'Verification service unavailable'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCaseClick = async (caseId: string) => {
    setLoading(true);
    try {
      const caseDetails = await legalService.getCaseDetails(caseId);
      setSelectedCase(caseDetails);
      setShowCaseDetails(true);
    } catch (error) {
      console.error('Failed to load case details:', error);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (activeTab === 'risk') {
      loadRiskAssessments();
    }
  }, [activeTab]);

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const tabs = [
    { id: 'search', label: 'Case Research', icon: Search },
    { id: 'analytics', label: 'Legal Analytics', icon: BarChart3 },
    { id: 'risk', label: 'Vendor Risk', icon: AlertTriangle },
    { id: 'attorney', label: 'Attorney Verification', icon: Shield },
    { id: 'documents', label: 'Document Analysis', icon: File }
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Scale className="h-8 w-8 text-blue-600" />
            Legal Intelligence
          </h1>
          <p className="text-gray-600 mt-2">
            Research case law, analyze legal trends, and assess vendor risks
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'search' && (
            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="flex-1">
                  <input
                    type="text"
                    placeholder="Search case law, precedents, or legal topics..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <button
                  onClick={handleSearch}
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                >
                  <Search className="h-4 w-4" />
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>

              {searchResults.length > 0 && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900">Search Results</h3>
                  {searchResults.map((result) => (
                    <div key={result.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                         onClick={() => handleCaseClick(result.id)}>
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold text-blue-600 hover:text-blue-800">
                          {result.title}
                        </h4>
                        <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                          {result.relevance}% match
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 mb-2">
                        <span className="font-medium">{result.court}</span> • {result.date}
                      </div>
                      <p className="text-gray-700">{result.excerpt}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-blue-50 p-6 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-blue-600 font-semibold">Total Cases Analyzed</p>
                      <p className="text-2xl font-bold text-blue-900">15,847</p>
                    </div>
                    <FileText className="h-8 w-8 text-blue-600" />
                  </div>
                </div>
                <div className="bg-green-50 p-6 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-green-600 font-semibold">Favorable Outcomes</p>
                      <p className="text-2xl font-bold text-green-900">78%</p>
                    </div>
                    <TrendingUp className="h-8 w-8 text-green-600" />
                  </div>
                </div>
                <div className="bg-purple-50 p-6 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-purple-600 font-semibold">Active Attorneys</p>
                      <p className="text-2xl font-bold text-purple-900">342</p>
                    </div>
                    <Users className="h-8 w-8 text-purple-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Legal Trends Analysis</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-gray-700">Contract Disputes</span>
                    <span className="text-red-600 font-semibold">↑ 15%</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-gray-700">Intellectual Property</span>
                    <span className="text-green-600 font-semibold">↓ 8%</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-gray-100">
                    <span className="text-gray-700">Employment Law</span>
                    <span className="text-blue-600 font-semibold">↑ 23%</span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-gray-700">Regulatory Compliance</span>
                    <span className="text-green-600 font-semibold">↓ 12%</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'risk' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">Vendor Risk Assessment</h3>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Run New Assessment
                </button>
              </div>

              <div className="space-y-4">
                {riskAssessments.map((assessment, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex justify-between items-start mb-4">
                      <h4 className="text-lg font-semibold text-gray-900">{assessment.vendor}</h4>
                      <div className="flex items-center gap-2">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(assessment.riskLevel)}`}>
                          {assessment.riskLevel.toUpperCase()} RISK
                        </span>
                        <span className="text-lg font-bold text-gray-900">{assessment.score}/100</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">Risk Factors:</p>
                      <ul className="list-disc list-inside space-y-1">
                        {assessment.factors.map((factor, idx) => (
                          <li key={idx} className="text-sm text-gray-600">{factor}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'attorney' && (
            <div className="space-y-6">
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Attorney Verification</h3>
                <div className="space-y-4">
                  <div className="flex gap-4">
                    <input
                      type="text"
                      placeholder="Enter attorney name or bar number..."
                      value={attorneyName}
                      onChange={(e) => setAttorneyName(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleAttorneyVerification()}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <button 
                      onClick={handleAttorneyVerification}
                      disabled={loading}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                      {loading ? 'Verifying...' : 'Verify'}
                    </button>
                  </div>
                  
                  {attorneyVerification && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                      {attorneyVerification.verified ? (
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Shield className="h-5 w-5 text-green-600" />
                            <span className="font-semibold text-green-800">Attorney Verified</span>
                          </div>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div><span className="font-medium">Name:</span> {attorneyVerification.attorney.name}</div>
                            <div><span className="font-medium">Bar Number:</span> {attorneyVerification.attorney.barNumber}</div>
                            <div><span className="font-medium">State:</span> {attorneyVerification.attorney.state}</div>
                            <div><span className="font-medium">Status:</span> {attorneyVerification.attorney.status}</div>
                            <div><span className="font-medium">Admission Date:</span> {attorneyVerification.attorney.admissionDate}</div>
                            <div><span className="font-medium">Disciplinary Record:</span> {attorneyVerification.attorney.disciplinaryRecord}</div>
                          </div>
                          <div className="mt-2">
                            <span className="font-medium">Practice Areas:</span>
                            <div className="flex flex-wrap gap-2 mt-1">
                              {attorneyVerification.attorney.practiceAreas.map((area: string, idx: number) => (
                                <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                                  {area}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="h-5 w-5 text-red-600" />
                          <span className="text-red-800">
                            {attorneyVerification.error || 'Attorney verification failed'}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600">
                      Verify attorney credentials, bar admissions, and disciplinary records.
                      Search across multiple state bar databases for comprehensive verification.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'documents' && (
            <div className="space-y-6">
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Document Analysis</h3>
                <DocumentAnalyzer />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Case Details Modal */}
      {showCaseDetails && selectedCase && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex justify-between items-center p-4 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Case Details</h2>
              <button
                onClick={() => setShowCaseDetails(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-4 overflow-y-auto max-h-full">
              <div className="space-y-6">
                {/* Case Header */}
                <div className="border-b border-gray-200 pb-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{selectedCase.title}</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Court:</span>
                      <span className="ml-2 text-gray-600">{selectedCase.court}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Date Filed:</span>
                      <span className="ml-2 text-gray-600">{selectedCase.date_filed}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Citation:</span>
                      <span className="ml-2 text-gray-600">{selectedCase.citation}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Status:</span>
                      <span className="ml-2 text-gray-600">{selectedCase.status}</span>
                    </div>
                  </div>
                  
                  {selectedCase.judges && selectedCase.judges.length > 0 && (
                    <div className="mt-2">
                      <span className="font-medium text-gray-700">Judges:</span>
                      <span className="ml-2 text-gray-600">{selectedCase.judges.join(', ')}</span>
                    </div>
                  )}
                </div>

                {/* Case Summary */}
                {selectedCase.summary && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Summary</h4>
                    <p className="text-gray-700">{selectedCase.summary}</p>
                  </div>
                )}

                {/* Full Text */}
                {selectedCase.full_text && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Full Text</h4>
                    <div className="bg-gray-50 p-4 rounded-lg max-h-60 overflow-y-auto">
                      <pre className="whitespace-pre-wrap text-sm text-gray-700">
                        {selectedCase.full_text.substring(0, 2000)}
                        {selectedCase.full_text.length > 2000 && '...'}
                      </pre>
                    </div>
                  </div>
                )}

                {/* External Link */}
                {selectedCase.url && (
                  <div className="flex justify-end">
                    <a
                      href={selectedCase.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      View on CourtListener
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LegalIntelligence;
