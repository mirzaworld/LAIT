import React, { useEffect } from 'react';
import { useDashboardMetrics, useInvoices } from '../hooks/useApi';

// Debug component to test API hooks
const DebugApiHooks: React.FC = () => {
  const { metrics, loading: metricsLoading, error: metricsError } = useDashboardMetrics();
  const { invoices, loading: invoicesLoading, error: invoicesError } = useInvoices();

  useEffect(() => {
    console.log('=== DEBUG API HOOKS ===');
    console.log('Metrics:', { metrics, loading: metricsLoading, error: metricsError });
    console.log('Invoices:', { invoices, loading: invoicesLoading, error: invoicesError });
  }, [metrics, metricsLoading, metricsError, invoices, invoicesLoading, invoicesError]);

  return (
    <div className="p-4 bg-gray-100 rounded-lg">
      <h2 className="text-lg font-bold mb-4">API Debug Information</h2>
      
      <div className="mb-4">
        <h3 className="font-semibold">Metrics Status:</h3>
        <p>Loading: {metricsLoading ? 'Yes' : 'No'}</p>
        <p>Error: {metricsError || 'None'}</p>
        <p>Data: {metrics ? 'Received' : 'None'}</p>
        {metrics && (
          <pre className="text-xs bg-white p-2 rounded mt-2">
            {JSON.stringify(metrics, null, 2)}
          </pre>
        )}
      </div>

      <div className="mb-4">
        <h3 className="font-semibold">Invoices Status:</h3>
        <p>Loading: {invoicesLoading ? 'Yes' : 'No'}</p>
        <p>Error: {invoicesError || 'None'}</p>
        <p>Data: {invoices.length} invoices</p>
        {invoices.length > 0 && (
          <pre className="text-xs bg-white p-2 rounded mt-2">
            {JSON.stringify(invoices[0], null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
};

export default DebugApiHooks;
