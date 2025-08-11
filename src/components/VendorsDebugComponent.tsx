import React, { useEffect, useState } from 'react';
import { useVendors } from '../hooks/useApi';
import { getVendors } from '../services/api';

const VendorsDebugComponent: React.FC = () => {
  const { vendors, loading, error } = useVendors();
  const [directAPIResult, setDirectAPIResult] = useState<any>(null);
  const [directAPIError, setDirectAPIError] = useState<string | null>(null);

  // Test direct API call
  useEffect(() => {
    const testDirectAPI = async () => {
      try {
        const result = await getVendors();
        setDirectAPIResult(result);
      } catch (err) {
        setDirectAPIError(err instanceof Error ? err.message : 'Direct API failed');
      }
    };
    testDirectAPI();
  }, []);

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: 'white', 
      border: '2px solid red',
      padding: '10px',
      zIndex: 9999,
      maxWidth: '400px',
      fontSize: '11px',
      maxHeight: '80vh',
      overflow: 'auto'
    }}>
      <h4>Vendors Debug</h4>
      
      <div style={{ marginBottom: '10px', borderBottom: '1px solid #ccc' }}>
        <strong>Hook State:</strong>
        <p>Loading: {loading ? 'Yes' : 'No'}</p>
        <p>Error: {error || 'None'}</p>
        <p>Vendors count: {vendors?.length || 0}</p>
        <p>Vendors is array: {Array.isArray(vendors) ? 'Yes' : 'No'}</p>
        <p>Vendors type: {typeof vendors}</p>
        {vendors && <p>First vendor: {JSON.stringify(vendors[0], null, 1)}</p>}
      </div>

      <div>
        <strong>Direct API:</strong>
        <p>Error: {directAPIError || 'None'}</p>
        <p>Result count: {directAPIResult?.length || 0}</p>
        <p>Result is array: {Array.isArray(directAPIResult) ? 'Yes' : 'No'}</p>
        <p>Result type: {typeof directAPIResult}</p>
        {directAPIResult && <p>First result: {JSON.stringify(directAPIResult[0], null, 1)}</p>}
      </div>
    </div>
  );
};

export default VendorsDebugComponent;
