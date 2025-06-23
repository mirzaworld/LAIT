import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, DollarSign, Activity, AlertTriangle, RefreshCw, 
  Brain, BarChart3, Users, Target, Zap, Eye, Clock, Globe,
  CheckCircle, XCircle, ArrowUp, ArrowDown, Minus
} from 'lucide-react';
import { 
  getLiveInsights, getLiveDataStatus, getMarketTrends, getRateBenchmarks,
  type LiveInsight, type LiveDataStatus, type MarketTrend, type RateBenchmark
} from '../services/api';

const LiveDashboardPanel: React.FC = () => {
  const [liveData, setLiveData] = useState<{
    insights: LiveInsight[];
    status: LiveDataStatus | null;
    trends: MarketTrend[];
    benchmarks: RateBenchmark[];
  }>({
    insights: [],
    status: null,
    trends: [],
    benchmarks: []
  });
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchLiveData = async () => {
    try {
      const [insights, status, trends, benchmarks] = await Promise.allSettled([
        getLiveInsights(10),
        getLiveDataStatus(),
        getMarketTrends(),
        getRateBenchmarks()
      ]);

      setLiveData({
        insights: insights.status === 'fulfilled' ? insights.value : [],
        status: status.status === 'fulfilled' ? status.value : null,
        trends: trends.status === 'fulfilled' ? trends.value : [],
        benchmarks: benchmarks.status === 'fulfilled' ? benchmarks.value : []
      });

      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching live data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveData();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchLiveData, 300000);
    return () => clearInterval(interval);
  }, []);

  const getInsightPriorityColor = (score: number) => {
    if (score >= 0.8) return 'border-l-red-500 bg-red-50';
    if (score >= 0.6) return 'border-l-orange-500 bg-orange-50';
    if (score >= 0.4) return 'border-l-yellow-500 bg-yellow-50';
    return 'border-l-green-500 bg-green-50';
  };

  const getTrendIcon = (score: number) => {
    if (score > 0.6) return <ArrowUp className="w-4 h-4 text-green-600" />;
    if (score < 0.4) return <ArrowDown className="w-4 h-4 text-red-600" />;
    return <Minus className="w-4 h-4 text-gray-600" />;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-600 mr-2" />
          <span className="text-gray-600">Loading live data...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Live Status Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-md p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Globe className="w-8 h-8 mr-3" />
            <div>
              <h2 className="text-2xl font-bold">Live Legal Intelligence</h2>
              <p className="text-blue-100">Real-time market insights and analytics</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-blue-100">Last Update</div>
            <div className="text-lg font-semibold">{lastUpdate.toLocaleTimeString()}</div>
            <button
              onClick={fetchLiveData}
              className="mt-2 px-3 py-1 bg-white bg-opacity-20 rounded-md hover:bg-opacity-30 transition-colors text-sm"
            >
              <RefreshCw className="w-4 h-4 inline mr-1" />
              Refresh
            </button>
          </div>
        </div>

        {/* Live Status Metrics */}
        {liveData.status && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="bg-white bg-opacity-10 rounded-lg p-4">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 mr-2" />
                <div>
                  <div className="text-sm text-blue-100">Service Status</div>
                  <div className="text-lg font-bold capitalize">{liveData.status.service_status}</div>
                </div>
              </div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-4">
              <div className="flex items-center">
                <Activity className="w-5 h-5 mr-2" />
                <div>
                  <div className="text-sm text-blue-100">Active Sources</div>
                  <div className="text-lg font-bold">{liveData.status.active_sources}/{liveData.status.total_sources}</div>
                </div>
              </div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-4">
              <div className="flex items-center">
                <Brain className="w-5 h-5 mr-2" />
                <div>
                  <div className="text-sm text-blue-100">Total Insights</div>
                  <div className="text-lg font-bold">{liveData.status.total_insights}</div>
                </div>
              </div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-4">
              <div className="flex items-center">
                <Clock className="w-5 h-5 mr-2" />
                <div>
                  <div className="text-sm text-blue-100">Recent (24h)</div>
                  <div className="text-lg font-bold">{liveData.status.recent_insights_24h}</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Live Insights and Trends Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Priority Insights */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <AlertTriangle className="w-5 h-5 text-orange-600 mr-2" />
              Priority Insights
            </h3>
            <span className="text-sm text-gray-500">{liveData.insights.length} insights</span>
          </div>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {liveData.insights.slice(0, 8).map((insight, index) => (
              <div 
                key={index} 
                className={`border-l-4 p-3 rounded-r-lg ${getInsightPriorityColor(insight.impact_score)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 text-sm mb-1">{insight.title}</h4>
                    <p className="text-gray-600 text-xs mb-2">{insight.content.substring(0, 120)}...</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">{insight.source}</span>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                          Impact: {(insight.impact_score * 100).toFixed(0)}%
                        </span>
                        <span className="text-xs bg-blue-100 px-2 py-1 rounded">
                          {insight.category}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Market Trends */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <TrendingUp className="w-5 h-5 text-green-600 mr-2" />
              Market Trends
            </h3>
            <span className="text-sm text-gray-500">{liveData.trends.length} trends</span>
          </div>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {liveData.trends.slice(0, 8).map((trend, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center flex-1">
                  {getTrendIcon(trend.trend_score)}
                  <div className="ml-3 flex-1">
                    <h4 className="font-medium text-gray-900 text-sm">{trend.trend_type}</h4>
                    <p className="text-gray-600 text-xs">{trend.description.substring(0, 80)}...</p>
                    <span className="text-xs text-gray-500">{trend.source}</span>
                  </div>
                </div>
                <div className={`px-2 py-1 rounded text-xs font-medium ${
                  trend.trend_score > 0.7 ? 'bg-green-100 text-green-800' :
                  trend.trend_score > 0.4 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {(trend.trend_score * 100).toFixed(0)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Rate Benchmarks */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <DollarSign className="w-5 h-5 text-blue-600 mr-2" />
            Live Rate Benchmarks
          </h3>
          <span className="text-sm text-gray-500">{liveData.benchmarks.length} benchmarks</span>
        </div>
        
        {liveData.benchmarks.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {liveData.benchmarks.slice(0, 6).map((benchmark, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900 text-sm">{benchmark.practice_area}</h4>
                  <span className="text-lg font-bold text-blue-600">{formatCurrency(benchmark.avg_rate)}</span>
                </div>
                <div className="text-xs text-gray-600 space-y-1">
                  <div>Level: {benchmark.seniority_level}</div>
                  <div>Market: {benchmark.market}</div>
                  <div>Source: {benchmark.source}</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <div>Rate benchmark data is being collected...</div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Zap className="w-5 h-5 text-purple-600 mr-2" />
          Quick Actions
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="flex items-center justify-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
            <Eye className="w-5 h-5 text-blue-600 mr-2" />
            <span className="text-blue-800 font-medium">View All Insights</span>
          </button>
          <button className="flex items-center justify-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
            <TrendingUp className="w-5 h-5 text-green-600 mr-2" />
            <span className="text-green-800 font-medium">Trend Analysis</span>
          </button>
          <button className="flex items-center justify-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
            <Users className="w-5 h-5 text-purple-600 mr-2" />
            <span className="text-purple-800 font-medium">Vendor Comparison</span>
          </button>
          <button className="flex items-center justify-center p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors">
            <Target className="w-5 h-5 text-orange-600 mr-2" />
            <span className="text-orange-800 font-medium">Market Reports</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default LiveDashboardPanel;
