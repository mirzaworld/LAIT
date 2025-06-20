import React, { useState } from 'react';
import { CheckCircle, XCircle, AlertTriangle, RefreshCw } from 'lucide-react';

const API_BASE = 'http://localhost:5003';

const ENDPOINTS = [
  { path: '/api/health', name: 'Health Check', method: 'GET' },
  { path: '/api/dashboard/metrics', name: 'Dashboard Metrics', method: 'GET' },
  { path: '/api/invoices', name: 'Invoices', method: 'GET' },
  { path: '/api/vendors', name: 'Vendors', method: 'GET' },
  { path: '/api/matters', name: 'Matters', method: 'GET' },
  { path: '/api/ml/test', name: 'ML Status', method: 'GET' },
  { path: '/api/workflow/electronic-billing', name: 'Workflow Status', method: 'GET' },
  { path: '/api/ml/anomaly-detection', name: 'Anomaly Detection', method: 'POST', body: {} },
  { path: '/api/ml/budget-forecast', name: 'Budget Forecast', method: 'POST', body: { matter_id: 'MAT-001', time_horizon: 6 } }
];

const ApiTester = () => {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState({ success: 0, failed: 0, total: 0, percentage: 0 });

  const testEndpoint = async (endpoint) => {
    try {
      const { path, method, body } = endpoint;
      
      const fetchOptions: RequestInit = {
        method,
        headers: { 'Content-Type': 'application/json' }
      };
      
      if (body) {
        fetchOptions.body = JSON.stringify(body);
      }
      
      const start = Date.now();
      const response = await fetch(`${API_BASE}${path}`, fetchOptions);
      const elapsed = Date.now() - start;
      
      if (response.ok) {
        const data = await response.json();
        return { success: true, data, elapsed };
      } else {
        const text = await response.text();
        return { success: false, error: text, status: response.status, elapsed };
      }
    } catch (error) {
      return { success: false, error: error.message, elapsed: 0 };
    }
  };

  const runAllTests = async () => {
    setLoading(true);
    const newResults = {};
    let success = 0;
    let failed = 0;
    
    for (const endpoint of ENDPOINTS) {
      const result = await testEndpoint(endpoint);
      newResults[endpoint.path] = { ...result, ...endpoint };
      
      if (result.success) success++;
      else failed++;
    }
    
    setResults(newResults);
    setSummary({ 
      success, 
      failed, 
      total: ENDPOINTS.length, 
      percentage: Math.round((success / ENDPOINTS.length) * 100) 
    });
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto bg-white rounded-lg shadow">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">LAIT API Diagnostics</h1>
        <button
          onClick={runAllTests}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Testing...
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4" />
              Test All Endpoints
            </>
          )}
        </button>
      </div>

      {Object.keys(results).length > 0 && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium">Summary</h2>
            <div className="flex items-center gap-4">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500 mr-1" />
                <span>{summary.success} Successful</span>
              </div>
              <div className="flex items-center">
                <XCircle className="w-5 h-5 text-red-500 mr-1" />
                <span>{summary.failed} Failed</span>
              </div>
            </div>
          </div>
          <div className="mt-2 bg-gray-200 rounded-full h-2.5">
            <div 
              className={`h-2.5 rounded-full ${summary.percentage === 100 ? 'bg-green-500' : 'bg-orange-500'}`}
              style={{ width: `${summary.percentage}%` }}
            ></div>
          </div>
          <div className="mt-2 text-sm text-gray-500 text-right">
            {summary.percentage}% successful
          </div>
        </div>
      )}

      <div className="space-y-4">
        {ENDPOINTS.map((endpoint) => {
          const result = results[endpoint.path];
          
          return (
            <div key={endpoint.path} className="border rounded-lg overflow-hidden">
              <div className="flex justify-between items-center p-4 bg-gray-50">
                <div>
                  <h3 className="font-medium">{endpoint.name}</h3>
                  <div className="text-sm text-gray-500 flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded ${endpoint.method === 'GET' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}`}>
                      {endpoint.method}
                    </span>
                    <span>{endpoint.path}</span>
                  </div>
                </div>
                
                {result && (
                  <div className="flex items-center">
                    {result.success ? (
                      <span className="flex items-center text-green-700">
                        <CheckCircle className="w-5 h-5 mr-1" />
                        OK ({result.elapsed}ms)
                      </span>
                    ) : (
                      <span className="flex items-center text-red-700">
                        <XCircle className="w-5 h-5 mr-1" />
                        Failed
                      </span>
                    )}
                  </div>
                )}
              </div>
              
              {result && !result.success && (
                <div className="p-4 bg-red-50 text-red-700 text-sm">
                  <strong>Error:</strong> {result.error}
                </div>
              )}
              
              {result && result.success && (
                <div className="p-4 border-t">
                  <div className="font-medium mb-1">Response:</div>
                  <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto max-h-48">
                    {JSON.stringify(result.data, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      {!loading && Object.keys(results).length === 0 && (
        <div className="flex flex-col items-center justify-center py-12 text-gray-500">
          <AlertTriangle className="w-12 h-12 mb-4 text-yellow-500" />
          <p>Click "Test All Endpoints" to begin diagnostics</p>
        </div>
      )}
    </div>
  );
};

export default ApiTester;
