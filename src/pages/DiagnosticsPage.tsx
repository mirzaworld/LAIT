import React from 'react';
import ApiDiagnostics from '../components/ApiDiagnostics';

const DiagnosticsPage: React.FC = () => {
  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">LAIT System Diagnostics</h1>
      
      <div className="space-y-6">
        <ApiDiagnostics />
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Advanced API Diagnostics</h2>
          <p className="mb-4">Run comprehensive API tests to ensure all endpoints are working properly.</p>
          
          <div className="flex space-x-4">
            <button 
              onClick={() => {
                const win = window.open('/api_diagnostics.html', '_blank');
                win?.focus();
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Run Browser Diagnostics
            </button>
            
            <button 
              onClick={() => {
                window.open('http://localhost:5003/api/health', '_blank');
              }}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Test Backend Health
            </button>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Environment Information</h2>
          <table className="min-w-full">
            <tbody>
              <tr className="border-b">
                <td className="py-2 font-medium">API URL</td>
                <td className="py-2">{import.meta.env.VITE_API_URL || 'http://localhost:5003'}</td>
              </tr>
              <tr className="border-b">
                <td className="py-2 font-medium">Environment</td>
                <td className="py-2">{import.meta.env.MODE}</td>
              </tr>
              <tr className="border-b">
                <td className="py-2 font-medium">Browser</td>
                <td className="py-2">{navigator.userAgent}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DiagnosticsPage;
