import React, { useState, useEffect } from 'react';

interface ResearchResult {
  id: string;
  type: string;
  title: string;
  status: 'completed' | 'pending' | 'error';
  result?: any;
  error?: string;
}

const LegalIntelligence: React.FC = () => {
  const [activeTab, setActiveTab] = useState('attorney-verification');
  const [loading, setLoading] = useState(false);
  const [researchResults, setResearchResults] = useState<ResearchResult[]>([]);

  const tabs = [
    { id: 'attorney-verification', name: 'Attorney Verification' },
    { id: 'case-research', name: 'Case Research' },
    { id: 'precedent-search', name: 'Precedent Search' },
    { id: 'judge-analysis', name: 'Judge Analysis' },
    { id: 'competitive-analysis', name: 'Competitive Analysis' },
    { id: 'court-analytics', name: 'Court Analytics' },
  ];

  const handleAttorneyVerification = async (formData: any) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('lait_token') || localStorage.getItem('token');
      const response = await fetch('/api/legal-intelligence/verify-attorney', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();
      
      setResearchResults(prev => [...prev, {
        id: Date.now().toString(),
        type: 'attorney-verification',
        title: `Verification: ${formData.attorney_name}`,
        status: response.ok ? 'completed' : 'error',
        result: response.ok ? result : undefined,
        error: !response.ok ? result.error : undefined
      }]);
    } catch (error) {
      console.error('Attorney verification error:', error);
      setResearchResults(prev => [...prev, {
        id: Date.now().toString(),
        type: 'attorney-verification',
        title: `Verification: ${formData.attorney_name}`,
        status: 'error',
        error: 'Network error occurred'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleCaseResearch = async (formData: any) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('lait_token') || localStorage.getItem('token');
      const response = await fetch('/api/legal-intelligence/comprehensive-research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();
      
      setResearchResults(prev => [...prev, {
        id: Date.now().toString(),
        type: 'case-research',
        title: `Research: ${formData.case_description.substring(0, 50)}...`,
        status: response.ok ? 'completed' : 'error',
        result: response.ok ? result : undefined,
        error: !response.ok ? result.error : undefined
      }]);
    } catch (error) {
      console.error('Case research error:', error);
      setResearchResults(prev => [...prev, {
        id: Date.now().toString(),
        type: 'case-research',
        title: `Research: ${formData.case_description.substring(0, 50)}...`,
        status: 'error',
        error: 'Network error occurred'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handlePrecedentSearch = async (formData: any) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('lait_token') || localStorage.getItem('token');
      const response = await fetch('/api/legal-intelligence/precedent-research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();
      
      setResearchResults(prev => [...prev, {
        id: Date.now().toString(),
        type: 'precedent-search',
        title: `Precedents: ${formData.legal_issue.substring(0, 50)}...`,
        status: response.ok ? 'completed' : 'error',
        result: response.ok ? result : undefined,
        error: !response.ok ? result.error : undefined
      }]);
    } catch (error) {
      console.error('Precedent search error:', error);
      setResearchResults(prev => [...prev, {
        id: Date.now().toString(),
        type: 'precedent-search',
        title: `Precedents: ${formData.legal_issue.substring(0, 50)}...`,
        status: 'error',
        error: 'Network error occurred'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const renderAttorneyVerificationForm = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">Attorney Verification</h3>
      <p className="text-sm text-gray-600">
        Verify attorney credentials and get background information using CourtListener data.
      </p>
      <form onSubmit={(e) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        handleAttorneyVerification({
          attorney_name: formData.get('attorney_name'),
          law_firm: formData.get('law_firm')
        });
      }}>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700">Attorney Name</label>
            <input
              type="text"
              name="attorney_name"
              required
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
              placeholder="John Smith"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Law Firm</label>
            <input
              type="text"
              name="law_firm"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
              placeholder="Smith & Associates"
            />
          </div>
        </div>
        <div className="mt-4">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? 'Verifying...' : 'Verify Attorney'}
          </button>
        </div>
      </form>
    </div>
  );

  const renderCaseResearchForm = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">Comprehensive Case Research</h3>
      <p className="text-sm text-gray-600">
        Research similar cases, relevant opinions, and docket information for your legal matter.
      </p>
      <form onSubmit={(e) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        handleCaseResearch({
          case_description: formData.get('case_description'),
          court: formData.get('court')
        });
      }}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Case Description</label>
            <textarea
              name="case_description"
              required
              rows={4}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
              placeholder="Describe the legal issue, claims, or case type..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Court (Optional)</label>
            <input
              type="text"
              name="court"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
              placeholder="e.g., Southern District of New York"
            />
          </div>
        </div>
        <div className="mt-4">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? 'Researching...' : 'Research Case'}
          </button>
        </div>
      </form>
    </div>
  );

  const renderPrecedentSearchForm = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">Legal Precedent Research</h3>
      <p className="text-sm text-gray-600">
        Search for legal precedents and analyze citation networks for specific legal issues.
      </p>
      <form onSubmit={(e) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        handlePrecedentSearch({
          legal_issue: formData.get('legal_issue'),
          jurisdiction: formData.get('jurisdiction')
        });
      }}>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Legal Issue</label>
            <textarea
              name="legal_issue"
              required
              rows={3}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
              placeholder="Describe the specific legal issue or doctrine..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Jurisdiction (Optional)</label>
            <input
              type="text"
              name="jurisdiction"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
              placeholder="e.g., ca9 (9th Circuit), scotus (Supreme Court)"
            />
          </div>
        </div>
        <div className="mt-4">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search Precedents'}
          </button>
        </div>
      </form>
    </div>
  );

  const renderResults = () => (
    <div className="mt-8">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Research Results</h3>
      {researchResults.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-gray-400 text-6xl mb-4">📊</div>
          <p className="text-gray-500">No research results yet. Submit a query above to get started.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {researchResults.map((result) => (
            <div key={result.id} className="bg-gray-50 rounded-lg p-4 border">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="mr-2">
                    {result.status === 'completed' && '✅'}
                    {result.status === 'error' && '❌'}
                    {result.status === 'pending' && '⏳'}
                  </span>
                  <h4 className="text-sm font-medium text-gray-900">{result.title}</h4>
                </div>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  result.status === 'completed' ? 'bg-green-100 text-green-800' :
                  result.status === 'error' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {result.status}
                </span>
              </div>
              
              {result.error && (
                <div className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded">
                  <strong>Error:</strong> {result.error}
                </div>
              )}
              
              {result.result && (
                <div className="mt-3 bg-white p-3 rounded border">
                  {result.type === 'attorney-verification' && (
                    <div className="text-sm">
                      <p><strong>Verified:</strong> {result.result.verified ? 'Yes' : 'No'}</p>
                      {result.result.attorney_info && (
                        <div className="mt-2 space-y-1">
                          <p><strong>Bar Admissions:</strong> {result.result.attorney_info.bar_admissions?.join(', ') || 'N/A'}</p>
                          <p><strong>Recent Cases:</strong> {result.result.attorney_info.recent_case_count || 0}</p>
                          {result.result.attorney_info.organizations && result.result.attorney_info.organizations.length > 0 && (
                            <p><strong>Organizations:</strong> {result.result.attorney_info.organizations.join(', ')}</p>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                  
                  {result.type === 'case-research' && (
                    <div className="text-sm space-y-2">
                      <p><strong>Summary:</strong> {result.result.summary}</p>
                      {result.result.findings?.similar_cases && (
                        <p><strong>Similar Cases Found:</strong> {result.result.findings.similar_cases.length}</p>
                      )}
                      {result.result.findings?.relevant_opinions && (
                        <p><strong>Relevant Opinions:</strong> {result.result.findings.relevant_opinions.length}</p>
                      )}
                      {result.result.findings?.similar_cases && result.result.findings.similar_cases.length > 0 && (
                        <div className="mt-2">
                          <strong>Sample Cases:</strong>
                          <ul className="list-disc list-inside ml-2 mt-1">
                            {result.result.findings.similar_cases.slice(0, 3).map((caseItem: any, index: number) => (
                              <li key={index} className="text-xs">
                                {caseItem.case_name} - {caseItem.court} ({caseItem.date_filed})
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {result.type === 'precedent-search' && (
                    <div className="text-sm space-y-2">
                      <p><strong>Precedents Found:</strong> {result.result.precedents?.length || 0}</p>
                      {result.result.insights && result.result.insights.length > 0 && (
                        <div>
                          <p><strong>Key Insights:</strong></p>
                          <ul className="list-disc list-inside ml-2">
                            {result.result.insights.map((insight: string, index: number) => (
                              <li key={index} className="text-xs">{insight}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {result.result.precedents && result.result.precedents.length > 0 && (
                        <div>
                          <strong>Sample Precedents:</strong>
                          <ul className="list-disc list-inside ml-2 mt-1">
                            {result.result.precedents.slice(0, 3).map((precedent: any, index: number) => (
                              <li key={index} className="text-xs">
                                {precedent.case_name} - {precedent.court} ({precedent.date_filed})
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'attorney-verification':
        return renderAttorneyVerificationForm();
      case 'case-research':
        return renderCaseResearchForm();
      case 'precedent-search':
        return renderPrecedentSearchForm();
      case 'judge-analysis':
        return (
          <div className="text-center py-8">
            <div className="text-gray-400 text-6xl mb-4">⚖️</div>
            <h3 className="text-lg font-medium text-gray-900">Judge Analysis</h3>
            <p className="text-sm text-gray-500 max-w-md mx-auto">
              Analyze judge patterns, tendencies, and background information to inform case strategy.
            </p>
            <p className="text-xs text-gray-400 mt-2">Coming soon</p>
          </div>
        );
      case 'competitive-analysis':
        return (
          <div className="text-center py-8">
            <div className="text-gray-400 text-6xl mb-4">📊</div>
            <h3 className="text-lg font-medium text-gray-900">Competitive Analysis</h3>
            <p className="text-sm text-gray-500 max-w-md mx-auto">
              Compare law firms and analyze competitive landscape using comprehensive legal data.
            </p>
            <p className="text-xs text-gray-400 mt-2">Coming soon</p>
          </div>
        );
      case 'court-analytics':
        return (
          <div className="text-center py-8">
            <div className="text-gray-400 text-6xl mb-4">🏛️</div>
            <h3 className="text-lg font-medium text-gray-900">Court Analytics</h3>
            <p className="text-sm text-gray-500 max-w-md mx-auto">
              Analyze court statistics, case patterns, and judicial trends for strategic insights.
            </p>
            <p className="text-xs text-gray-400 mt-2">Coming soon</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900">Legal Intelligence</h1>
        <p className="mt-2 text-sm text-gray-600">
          Research attorneys, cases, precedents, and competitive intelligence using CourtListener data.
          Enhance your legal spend optimization with comprehensive legal research capabilities.
        </p>
        
        {/* Feature highlights */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="font-medium text-blue-900">Attorney Verification</div>
            <div className="text-xs text-blue-700">Verify credentials and case history</div>
          </div>
          <div className="bg-green-50 p-3 rounded-lg">
            <div className="font-medium text-green-900">Case Research</div>
            <div className="text-xs text-green-700">Find similar cases and opinions</div>
          </div>
          <div className="bg-purple-50 p-3 rounded-lg">
            <div className="font-medium text-purple-900">Precedent Analysis</div>
            <div className="text-xs text-purple-700">Legal precedents and citations</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {renderTabContent()}
        </div>
      </div>

      {/* Results */}
      {renderResults()}
    </div>
  );
};

export default LegalIntelligence;
