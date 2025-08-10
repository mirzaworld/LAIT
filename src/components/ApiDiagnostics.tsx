import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react';

interface EndpointStatus {
  endpoint: string;
  description: string;
  status: 'success' | 'error' | 'loading';
  responseTime?: number;
  errorMessage?: string;
}

const ApiDiagnostics: React.FC = () => {
  const [endpoints, setEndpoints] = useState<EndpointStatus[]>([
    { endpoint: '/api/health', description: 'Health Check', status: 'loading' },
    { endpoint: '/api/self-test', description: 'Self Test', status: 'loading' },
    { endpoint: '/api/dashboard/metrics', description: 'Dashboard Metrics', status: 'loading' },
    { endpoint: '/api/invoices', description: 'Invoices List', status: 'loading' },
    { endpoint: '/api/vendors', description: 'Vendors List', status: 'loading' },
    { endpoint: '/api/matters', description: 'Matters List', status: 'loading' },
    { endpoint: '/api/ml/test', description: 'ML Service', status: 'loading' },
    { endpoint: '/api/ml/anomaly-detection', description: 'Anomaly Detection', status: 'loading' },
    { endpoint: '/api/workflow/electronic-billing', description: 'Workflow Status', status: 'loading' },
  ]);
  const [isRunning, setIsRunning] = useState(false);
  const [apiUrl, setApiUrl] = useState(import.meta.env.VITE_API_URL || 'http://localhost:5003');

  const testEndpoints = async () => {
    setIsRunning(true);
    
    // Create a copy of endpoints to update
    const updatedEndpoints = [...endpoints];
    
    // Test each endpoint
    for (let i = 0; i < updatedEndpoints.length; i++) {
      const endpoint = updatedEndpoints[i];
      endpoint.status = 'loading';
      setEndpoints([...updatedEndpoints]);
      
      try {
        const startTime = performance.now();
        const response = await fetch(`${apiUrl}${endpoint.endpoint}`);
        const endTime = performance.now();
        
        if (response.ok) {
          endpoint.status = 'success';
          endpoint.responseTime = Math.round(endTime - startTime);
          endpoint.errorMessage = undefined;
        } else {
          endpoint.status = 'error';
          endpoint.errorMessage = `Status: ${response.status} ${response.statusText}`;
        }
      } catch (error) {
        endpoint.status = 'error';
        endpoint.errorMessage = error instanceof Error ? error.message : 'Unknown error';
      }
      
      setEndpoints([...updatedEndpoints]);
      // Add a small delay between requests to prevent overwhelming the server
      await new Promise(resolve => setTimeout(resolve, 300));
    }
    
    setIsRunning(false);
  };

  useEffect(() => {
    testEndpoints();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">API Connection Diagnostics</h2>
        <div className="flex items-center space-x-4">
          <input
            type="text"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            placeholder="API URL"
          />
          <button
            onClick={testEndpoints}
            disabled={isRunning}
            className="px-4 py-2 bg-blue-500 text-white rounded-md flex items-center space-x-2 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isRunning ? 'animate-spin' : ''}`} />
            <span>Test Connections</span>
          </button>
        </div>
      </div>

      <div className="rounded-lg border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Endpoint
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Description
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Response Time
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {endpoints.map((endpoint, index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono">{endpoint.endpoint}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{endpoint.description}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    {endpoint.status === 'loading' && (
                      <div className="w-4 h-4 border-2 border-gray-200 border-t-blue-500 rounded-full animate-spin mr-2"></div>
                    )}
                    {endpoint.status === 'success' && (
                      <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    )}
                    {endpoint.status === 'error' && (
                      <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
                    )}
                    <span
                      className={`text-sm ${
                        endpoint.status === 'success'
                          ? 'text-green-500'
                          : endpoint.status === 'error'
                          ? 'text-red-500'
                          : 'text-gray-500'
                      }`}
                    >
                      {endpoint.status.charAt(0).toUpperCase() + endpoint.status.slice(1)}
                    </span>
                  </div>
                  {endpoint.errorMessage && (
                    <p className="mt-1 text-xs text-red-500">{endpoint.errorMessage}</p>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  {endpoint.responseTime ? `${endpoint.responseTime}ms` : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <h3 className="font-medium text-blue-800 mb-2">Troubleshooting Tips:</h3>
        <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
          <li>Make sure the backend API is running on the specified URL</li>
          <li>Check CORS settings if you see Access-Control-Allow-Origin errors</li>
          <li>Verify network connectivity and firewall settings</li>
          <li>Inspect browser console for detailed error messages</li>
          <li>Ensure your .env file has the correct VITE_API_URL set</li>
        </ul>
      </div>
    </div>
  );
};

export default ApiDiagnostics;
