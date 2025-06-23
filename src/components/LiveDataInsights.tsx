import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, TrendingUp, Globe, RefreshCw, CheckCircle, XCircle } from 'lucide-react';

interface LiveDataInsight {
  type: string;
  message: string;
  impact: 'high' | 'medium' | 'low';
  recommendation: string;
  source: string;
}

interface LiveDataStatus {
  service_status: string;
  total_sources: number;
  active_sources: number;
  connected_sources: number;
  last_update: string | null;
}

const LiveDataInsights: React.FC = () => {
  const [insights, setInsights] = useState<LiveDataInsight[]>([]);
  const [status, setStatus] = useState<LiveDataStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchLiveData = async () => {
    try {
      setLoading(true);
      
      // Fetch live data status
      const statusResponse = await fetch('/api/live-data/status');
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setStatus(statusData);
      }

      // Fetch live insights
      const insightsResponse = await fetch('/api/live-data/insights');
      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setInsights(insightsData.insights || []);
      }

      setError(null);
      setLastRefresh(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch live data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveData();
    
    // Set up auto-refresh every 5 minutes
    const interval = setInterval(fetchLiveData, 300000);
    return () => clearInterval(interval);
  }, []);

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getImpactIcon = (impact: string) => {
    switch (impact) {
      case 'high': return <AlertTriangle className="w-4 h-4" />;
      case 'medium': return <TrendingUp className="w-4 h-4" />;
      case 'low': return <CheckCircle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <div className="flex items-center justify-center">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-600">Loading live data insights...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Status Header */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Globe className="w-6 h-6 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Live Legal Data Feed</h3>
          </div>
          <button
            onClick={fetchLiveData}
            className="flex items-center px-3 py-1 text-sm bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors"
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            Refresh
          </button>
        </div>

        {status && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className={`inline-flex items-center px-2 py-1 rounded-full text-sm ${
                status.service_status === 'operational' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              }`}>
                {status.service_status === 'operational' ? <CheckCircle className="w-4 h-4 mr-1" /> : <XCircle className="w-4 h-4 mr-1" />}
                {status.service_status}
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{status.connected_sources}</div>
              <div className="text-sm text-gray-500">Connected Sources</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{status.total_sources}</div>
              <div className="text-sm text-gray-500">Total Sources</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-900">
                {status.last_update ? new Date(status.last_update).toLocaleTimeString() : 'Never'}
              </div>
              <div className="text-sm text-gray-500">Last Update</div>
            </div>
          </div>
        )}

        <div className="mt-4 text-xs text-gray-500">
          Last refreshed: {lastRefresh.toLocaleTimeString()}
        </div>
      </div>

      {/* Insights */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Real-Time Legal Insights</h4>
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <div className="flex items-center">
              <XCircle className="w-5 h-5 text-red-600 mr-2" />
              <span className="text-red-700">{error}</span>
            </div>
          </div>
        )}

        {insights.length === 0 ? (
          <div className="text-center py-8">
            <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No live insights available at the moment</p>
            <p className="text-sm text-gray-400 mt-1">
              {status?.service_status !== 'operational' 
                ? 'Live data service is currently unavailable' 
                : 'Check back later for real-time updates'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {insights.slice(0, 10).map((insight, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(insight.impact)}`}>
                        {getImpactIcon(insight.impact)}
                        <span className="ml-1 capitalize">{insight.impact} Impact</span>
                      </span>
                      <span className="ml-2 text-xs text-gray-500">{insight.source}</span>
                    </div>
                    <h5 className="font-medium text-gray-900 mb-1">{insight.message}</h5>
                    <p className="text-sm text-gray-600">{insight.recommendation}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveDataInsights;
