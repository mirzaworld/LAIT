import React, { useState, useEffect } from 'react';

const ApiDebugComponent: React.FC = () => {
  const [debugInfo, setDebugInfo] = useState<any>({});
  const [loading, setLoading] = useState(false);

  const testApi = async () => {
    setLoading(true);
    const results: any = {};

    // Test environment variables
    results.env = {
      VITE_API_URL: import.meta.env.VITE_API_URL,
      DEV: import.meta.env.DEV,
      PROD: import.meta.env.PROD,
      MODE: import.meta.env.MODE
    };

    // Test API URL construction
    const API_URL = import.meta.env.VITE_API_URL || '';
    const apiUrl = (path: string) => {
      if (import.meta.env.DEV || !API_URL) {
        return path;
      }
      if (API_URL) {
        const baseUrl = API_URL.replace(/\/api$/, '');
        return `${baseUrl}${path}`;
      }
      return path;
    };

    results.apiUrlTest = {
      dashboardPath: apiUrl('/api/dashboard/metrics'),
      healthPath: apiUrl('/api/health')
    };

    // Test actual API call
    try {
      const response = await fetch('/api/dashboard/metrics', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': 'Bearer mock-jwt-token-for-development'
        }
      });

      results.fetchTest = {
        status: response.status,
        ok: response.ok,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries())
      };

      if (response.ok) {
        results.fetchTest.data = await response.json();
      } else {
        results.fetchTest.error = await response.text();
      }
    } catch (error) {
      results.fetchTest = {
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }

    setDebugInfo(results);
    setLoading(false);
  };

  useEffect(() => {
    testApi();
  }, []);

  return (
    <div className="fixed top-0 right-0 w-96 h-screen overflow-y-auto bg-white border-l border-gray-300 p-4 z-50 font-mono text-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-lg">API Debug</h3>
        <button 
          onClick={testApi} 
          disabled={loading}
          className="px-3 py-1 bg-blue-500 text-white rounded disabled:opacity-50"
        >
          {loading ? 'Testing...' : 'Retest'}
        </button>
      </div>
      
      <div className="space-y-4">
        <div>
          <h4 className="font-semibold text-green-600">Environment</h4>
          <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-x-auto">
            {JSON.stringify(debugInfo.env, null, 2)}
          </pre>
        </div>

        <div>
          <h4 className="font-semibold text-blue-600">API URL Construction</h4>
          <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-x-auto">
            {JSON.stringify(debugInfo.apiUrlTest, null, 2)}
          </pre>
        </div>

        <div>
          <h4 className="font-semibold text-purple-600">Fetch Test</h4>
          <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-x-auto">
            {JSON.stringify(debugInfo.fetchTest, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default ApiDebugComponent;
