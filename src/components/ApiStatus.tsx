import React, { useState, useEffect } from 'react';

interface ApiStatusProps {
  url?: string;
  label?: string;
  className?: string;
}

/**
 * Component that checks the status of an API endpoint and displays the result
 */
const ApiStatus: React.FC<ApiStatusProps> = ({ 
  url = '/api/health', 
  label = 'API Status',
  className = ''
}) => {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [message, setMessage] = useState<string>('Checking connection...');

  useEffect(() => {
    const checkApiStatus = async () => {
      setStatus('loading');
      setMessage('Checking connection...');
      
      try {
        const startTime = performance.now();
        const response = await fetch(url, { 
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        const endTime = performance.now();
        
        setResponseTime(Math.round(endTime - startTime));
        
        if (response.ok) {
          setStatus('success');
          setMessage('Connected');
        } else {
          setStatus('error');
          setMessage(`Error: ${response.status}`);
        }
      } catch (error) {
        setStatus('error');
        setMessage('Connection failed');
        console.error('API connection check failed:', error);
      }
    };
    
    checkApiStatus();
  }, [url]);
  
  const getStatusIcon = () => {
    switch(status) {
      case 'success':
        return (
          <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'error':
        return (
          <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5 text-yellow-500 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        );
    }
  };
  
  const getStatusClass = () => {
    switch(status) {
      case 'success': return 'bg-green-100 text-green-800 border-green-200';
      case 'error': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    }
  };
  
  return (
    <div className={`inline-flex items-center rounded-full px-3 py-1 text-sm border ${getStatusClass()} ${className}`}>
      {getStatusIcon()}
      <span className="ml-2 font-medium">{label}:</span>
      <span className="ml-1">{message}</span>
      {responseTime !== null && status === 'success' && (
        <span className="ml-1 text-gray-500">({responseTime}ms)</span>
      )}
    </div>
  );
};

export default ApiStatus;
