import React, { useState, useEffect } from 'react';
import { getDashboardMetrics, getVendors, getInvoices, getSpendTrends } from '../services/api';

const ApiDebugPanel: React.FC = () => {
  const [debug, setDebug] = useState<any>({});

  useEffect(() => {
    const testApis = async () => {
      const results: any = {};
      
      try {
        console.log('Testing dashboard metrics...');
        const metrics = await getDashboardMetrics();
        results.metrics = { success: true, data: metrics };
      } catch (error) {
        results.metrics = { success: false, error: error.message };
      }

      try {
        console.log('Testing vendors...');
        const vendors = await getVendors();
        results.vendors = { success: true, data: vendors };
      } catch (error) {
        results.vendors = { success: false, error: error.message };
      }

      try {
        console.log('Testing invoices...');
        const invoices = await getInvoices();
        results.invoices = { success: true, data: invoices };
      } catch (error) {
        results.invoices = { success: false, error: error.message };
      }

      try {
        console.log('Testing spend trends...');
        const trends = await getSpendTrends();
        results.trends = { success: true, data: trends };
      } catch (error) {
        results.trends = { success: false, error: error.message };
      }

      setDebug(results);
    };

    testApis();
  }, []);

  return (
    <div className="bg-gray-100 p-4 m-4 rounded-lg">
      <h3 className="text-lg font-semibold mb-4">API Debug Panel</h3>
      {Object.entries(debug).map(([key, result]: [string, any]) => (
        <div key={key} className="mb-4">
          <h4 className="font-medium">{key}</h4>
          <div className={`p-2 rounded ${result.success ? 'bg-green-100' : 'bg-red-100'}`}>
            {result.success ? (
              <div>
                <span className="text-green-600">✓ Success</span>
                <details className="mt-2">
                  <summary>Data</summary>
                  <pre className="text-xs overflow-auto">
                    {JSON.stringify(result.data, null, 2)}
                  </pre>
                </details>
              </div>
            ) : (
              <span className="text-red-600">✗ Error: {result.error}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ApiDebugPanel;
