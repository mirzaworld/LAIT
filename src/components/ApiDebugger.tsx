import React, { useEffect, useState } from 'react';
import { getDashboardMetrics } from '../services/api';

const ApiDebugger: React.FC = () => {
  const [debug, setDebug] = useState<any>({});

  useEffect(() => {
    const testApi = async () => {
      try {
        console.log('Testing API call...');
        const data = await getDashboardMetrics();
        console.log('API Success:', data);
        setDebug({ success: true, data });
      } catch (error) {
        console.error('API Error:', error);
        setDebug({ success: false, error: error.message });
      }
    };

    testApi();
  }, []);

  return (
    <div className="fixed top-4 right-4 p-4 bg-yellow-100 border border-yellow-400 rounded z-50 max-w-md">
      <h3 className="font-bold">API Debug</h3>
      <pre className="text-xs mt-2 overflow-auto max-h-32">
        {JSON.stringify(debug, null, 2)}
      </pre>
    </div>
  );
};

export default ApiDebugger;
