import React, { useState, useEffect } from 'react';
import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

type ApiStatus = 'online' | 'offline' | 'degraded' | 'checking';

interface ApiHealthIndicatorProps {
  className?: string;
  apiUrl?: string;
}

const ApiHealthIndicator: React.FC<ApiHealthIndicatorProps> = ({ 
  className = '',
  apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5003'
}) => {
  const [status, setStatus] = useState<ApiStatus>('checking');
  const [lastChecked, setLastChecked] = useState<Date>(new Date());
  const [showDetails, setShowDetails] = useState(false);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const checkApiHealth = async () => {
    setStatus('checking');
    try {
      const startTime = performance.now();
      const response = await fetch(`${apiUrl}/api/health`, { 
        method: 'GET',
        cache: 'no-cache',
        headers: { 'Content-Type': 'application/json' }
      });
      const endTime = performance.now();
      setResponseTime(Math.round(endTime - startTime));
      
      if (response.ok) {
        setStatus('online');
        setErrorMessage(null);
      } else {
        setStatus('degraded');
        setErrorMessage(`API responded with status ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      setStatus('offline');
      setErrorMessage(error instanceof Error ? error.message : 'Unknown error');
      setResponseTime(null);
    } finally {
      setLastChecked(new Date());
    }
  };
  
  useEffect(() => {
    // Check health immediately and then every 30 seconds
    checkApiHealth();
    const interval = setInterval(checkApiHealth, 30000);
    
    return () => {
      clearInterval(interval);
    };
  }, [apiUrl]);
  
  const getStatusIcon = () => {
    switch (status) {
      case 'online':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'degraded':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'offline':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'checking':
      default:
        return (
          <div className="w-4 h-4 rounded-full border-2 border-gray-300 border-t-blue-500 animate-spin"></div>
        );
    }
  };
  
  const getStatusColor = () => {
    switch (status) {
      case 'online': return 'bg-green-100 text-green-800 border-green-200';
      case 'degraded': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'offline': return 'bg-red-100 text-red-800 border-red-200';
      case 'checking':
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };
  
  const getStatusText = () => {
    switch (status) {
      case 'online': return 'API Online';
      case 'degraded': return 'API Degraded';
      case 'offline': return 'API Offline';
      case 'checking':
      default: return 'Checking API...';
    }
  };
  
  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setShowDetails(!showDetails)}
        className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor()}`}
      >
        {getStatusIcon()}
        <span>{getStatusText()}</span>
      </button>
      
      {showDetails && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg border border-gray-200 z-50">
          <div className="p-3">
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-medium">API Status</h3>
              <button 
                onClick={checkApiHealth}
                className="text-xs text-blue-600 hover:text-blue-800 flex items-center"
              >
                Refresh
              </button>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className={`font-medium ${
                  status === 'online' ? 'text-green-600' : 
                  status === 'degraded' ? 'text-yellow-600' : 
                  status === 'offline' ? 'text-red-600' : 'text-gray-600'
                }`}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </span>
              </div>
              
              {responseTime !== null && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Response Time:</span>
                  <span className="font-medium">{responseTime} ms</span>
                </div>
              )}
              
              <div className="flex justify-between">
                <span className="text-gray-600">Last Checked:</span>
                <span className="font-medium">
                  {lastChecked.toLocaleTimeString()}
                </span>
              </div>
              
              {errorMessage && (
                <div className="mt-2 p-2 bg-red-50 border border-red-100 rounded text-red-700 text-xs">
                  {errorMessage}
                </div>
              )}
              
              <div className="mt-2 text-xs text-gray-500">
                URL: {apiUrl}/api/health
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiHealthIndicator;
