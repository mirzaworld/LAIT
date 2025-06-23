import React, { useState, useEffect } from 'react';
import { 
  Activity, AlertTriangle, TrendingUp, Globe, RefreshCw, CheckCircle, XCircle, 
  BarChart3, Users, DollarSign, Calendar, Clock, ExternalLink, Zap,
  Brain, Target, PieChart, LineChart, Eye, Database, Wifi, WifiOff
} from 'lucide-react';
import { 
  getLiveDataSources, getLiveInsights, getRateBenchmarks, getMarketTrends, 
  getLiveDataStatus, triggerLiveDataCollection, getCourtData, getLegalMarketAnalysis,
  type LiveDataSource, type LiveInsight, type RateBenchmark, type MarketTrend, type LiveDataStatus
} from '../services/api';

const LiveDataInsights: React.FC = () => {
  const [insights, setInsights] = useState<LiveInsight[]>([]);
  const [sources, setSources] = useState<LiveDataSource[]>([]);
  const [rateBenchmarks, setRateBenchmarks] = useState<RateBenchmark[]>([]);
  const [marketTrends, setMarketTrends] = useState<MarketTrend[]>([]);
  const [courtData, setCourtData] = useState<any>(null);
  const [marketAnalysis, setMarketAnalysis] = useState<any>(null);
  const [status, setStatus] = useState<LiveDataStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [activeTab, setActiveTab] = useState<'overview' | 'insights' | 'rates' | 'trends' | 'sources' | 'court' | 'market'>('overview');

  const fetchLiveData = async (force = false) => {
    try {
      if (force) setRefreshing(true);
      else setLoading(true);
      
      // Fetch all live data in parallel
      const [
        statusData,
        sourcesData,
        insightsData,
        rateBenchmarksData,
        trendsData,
        courtDataResponse,
        marketAnalysisData
      ] = await Promise.allSettled([
        getLiveDataStatus(),
        getLiveDataSources(),
        getLiveInsights(50),
        getRateBenchmarks(),
        getMarketTrends(),
        getCourtData(),
        getLegalMarketAnalysis()
      ]);

      // Process successful responses
      if (statusData.status === 'fulfilled') setStatus(statusData.value);
      if (sourcesData.status === 'fulfilled') setSources(sourcesData.value.sources || []);
      if (insightsData.status === 'fulfilled') setInsights(insightsData.value || []);
      if (rateBenchmarksData.status === 'fulfilled') setRateBenchmarks(rateBenchmarksData.value || []);
      if (trendsData.status === 'fulfilled') setMarketTrends(trendsData.value || []);
      if (courtDataResponse.status === 'fulfilled') setCourtData(courtDataResponse.value);
      if (marketAnalysisData.status === 'fulfilled') setMarketAnalysis(marketAnalysisData.value);

      setError(null);
      setLastRefresh(new Date());
    } catch (err) {
      console.error('Error fetching live data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch live data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    await triggerLiveDataCollection();
    await fetchLiveData(true);
  };

  useEffect(() => {
    fetchLiveData();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(() => fetchLiveData(true), 300000);
    return () => clearInterval(interval);
  }, []);

  const getImpactColor = (impact: number) => {
    if (impact >= 0.8) return 'text-red-600 bg-red-50';
    if (impact >= 0.6) return 'text-orange-600 bg-orange-50';
    if (impact >= 0.4) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'spending_trends': return <TrendingUp className="w-4 h-4" />;
      case 'rate_benchmarks': return <DollarSign className="w-4 h-4" />;
      case 'market_trends': return <BarChart3 className="w-4 h-4" />;
      case 'technology_trends': return <Brain className="w-4 h-4" />;
      case 'regulatory_updates': return <AlertTriangle className="w-4 h-4" />;
      case 'legal_tech': return <Zap className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading && !status) {
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
      {/* Header with Status */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Globe className="w-6 h-6 text-blue-600 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900">Live Legal Data Intelligence</h2>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center text-sm text-gray-500">
              <Clock className="w-4 h-4 mr-1" />
              Last updated: {formatDate(lastRefresh.toISOString())}
            </div>
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 mr-1 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Status Overview */}
        {status && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                <div>
                  <div className="text-sm text-green-600 font-medium">Service Status</div>
                  <div className="text-lg font-semibold text-green-800 capitalize">{status.service_status}</div>
                </div>
              </div>
            </div>
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center">
                <Database className="w-5 h-5 text-blue-600 mr-2" />
                <div>
                  <div className="text-sm text-blue-600 font-medium">Active Sources</div>
                  <div className="text-lg font-semibold text-blue-800">{status.active_sources}/{status.total_sources}</div>
                </div>
              </div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center">
                <Brain className="w-5 h-5 text-purple-600 mr-2" />
                <div>
                  <div className="text-sm text-purple-600 font-medium">Total Insights</div>
                  <div className="text-lg font-semibold text-purple-800">{status.total_insights}</div>
                </div>
              </div>
            </div>
            <div className="bg-orange-50 rounded-lg p-4">
              <div className="flex items-center">
                <Activity className="w-5 h-5 text-orange-600 mr-2" />
                <div>
                  <div className="text-sm text-orange-600 font-medium">Recent (24h)</div>
                  <div className="text-lg font-semibold text-orange-800">{status.recent_insights_24h}</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'insights', label: 'Live Insights', icon: Brain },
            { id: 'rates', label: 'Rate Benchmarks', icon: DollarSign },
            { id: 'trends', label: 'Market Trends', icon: TrendingUp },
            { id: 'court', label: 'Court Data', icon: Target },
            { id: 'market', label: 'Market Analysis', icon: BarChart3 },
            { id: 'sources', label: 'Data Sources', icon: Globe }
          ].map(tab => {
            const IconComponent = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <IconComponent className="w-4 h-4 mr-1" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Insights Preview */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Insights</h3>
            <div className="space-y-3">
              {insights.slice(0, 5).map((insight, index) => (
                <div key={index} className="flex items-start p-3 bg-gray-50 rounded-lg">
                  <div className={`p-1 rounded ${getImpactColor(insight.impact_score)} mr-3`}>
                    {getCategoryIcon(insight.category)}
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 text-sm">{insight.title}</div>
                    <div className="text-gray-600 text-xs mt-1">{insight.content.substring(0, 100)}...</div>
                    <div className="text-xs text-gray-500 mt-1">{insight.source}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Market Trends Preview */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Trends</h3>
            <div className="space-y-3">
              {marketTrends.slice(0, 5).map((trend, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 text-sm">{trend.trend_type}</div>
                    <div className="text-gray-600 text-xs mt-1">{trend.description}</div>
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
      )}

      {activeTab === 'insights' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Live Legal Industry Insights</h3>
          <div className="space-y-4">
            {insights.map((insight, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start">
                    <div className={`p-2 rounded-lg ${getImpactColor(insight.impact_score)} mr-4`}>
                      {getCategoryIcon(insight.category)}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900 mb-2">{insight.title}</h4>
                      <p className="text-gray-600 mb-3">{insight.content}</p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span>Source: {insight.source}</span>
                          <span>Category: {insight.category}</span>
                          <span>{formatDate(insight.created_at)}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-gray-500">Impact: {(insight.impact_score * 100).toFixed(0)}%</span>
                          <span className="text-xs text-gray-500">Relevance: {(insight.relevance_score * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'rates' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Live Rate Benchmarks</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Practice Area</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Seniority</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Average Rate</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Market</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {rateBenchmarks.map((benchmark, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{benchmark.practice_area}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{benchmark.seniority_level}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatCurrency(benchmark.avg_rate)}/hr</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{benchmark.market}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{benchmark.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'trends' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Trends Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {marketTrends.map((trend, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-gray-900">{trend.trend_type}</h4>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                    trend.trend_score > 0.7 ? 'bg-green-100 text-green-800' :
                    trend.trend_score > 0.4 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {(trend.trend_score * 100).toFixed(0)}%
                  </div>
                </div>
                <p className="text-gray-600 text-sm mb-3">{trend.description}</p>
                <div className="text-xs text-gray-500">
                  Source: {trend.source} • {formatDate(trend.created_at)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'court' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Court Data & Legal Intelligence</h3>
          {courtData ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-blue-800">{courtData.recent_cases || 'N/A'}</div>
                  <div className="text-sm text-blue-600">Recent Cases</div>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-green-800">{courtData.active_litigation || 'N/A'}</div>
                  <div className="text-sm text-green-600">Active Litigation</div>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-purple-800">{courtData.avg_settlement || 'N/A'}</div>
                  <div className="text-sm text-purple-600">Avg Settlement</div>
                </div>
              </div>
              {courtData.insights && (
                <div className="mt-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Key Insights</h4>
                  <div className="space-y-2">
                    {courtData.insights.map((insight: string, index: number) => (
                      <div key={index} className="flex items-start">
                        <Target className="w-4 h-4 text-blue-600 mr-2 mt-0.5" />
                        <span className="text-gray-700 text-sm">{insight}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Target className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <div>Court data is being collected...</div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'market' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Legal Market Analysis</h3>
          {marketAnalysis ? (
            <div className="space-y-6">
              {marketAnalysis.spending_trends && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Spending Trends</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-green-50 rounded-lg p-4">
                      <div className="text-xl font-bold text-green-800">{marketAnalysis.spending_trends.growth_rate}%</div>
                      <div className="text-sm text-green-600">Annual Growth</div>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-4">
                      <div className="text-xl font-bold text-blue-800">{formatCurrency(marketAnalysis.spending_trends.avg_spend)}</div>
                      <div className="text-sm text-blue-600">Average Spend</div>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-4">
                      <div className="text-xl font-bold text-purple-800">{marketAnalysis.spending_trends.efficiency_gain}%</div>
                      <div className="text-sm text-purple-600">Efficiency Gain</div>
                    </div>
                    <div className="bg-orange-50 rounded-lg p-4">
                      <div className="text-xl font-bold text-orange-800">{marketAnalysis.spending_trends.ai_adoption}%</div>
                      <div className="text-sm text-orange-600">AI Adoption</div>
                    </div>
                  </div>
                </div>
              )}
              {marketAnalysis.recommendations && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Strategic Recommendations</h4>
                  <div className="space-y-2">
                    {marketAnalysis.recommendations.map((rec: string, index: number) => (
                      <div key={index} className="flex items-start p-3 bg-blue-50 rounded-lg">
                        <CheckCircle className="w-4 h-4 text-blue-600 mr-2 mt-0.5" />
                        <span className="text-blue-900 text-sm">{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <div>Market analysis is being processed...</div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'sources' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Sources Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sources.map((source, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{source.name}</h4>
                  <div className="flex items-center">
                    {source.status === 'active' ? (
                      <Wifi className="w-4 h-4 text-green-600" />
                    ) : (
                      <WifiOff className="w-4 h-4 text-red-600" />
                    )}
                  </div>
                </div>
                <div className="space-y-1 text-sm text-gray-600">
                  <div>Type: {source.data_type}</div>
                  <div>Update: {source.update_frequency}</div>
                  <div className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                    source.status === 'active' ? 'bg-green-100 text-green-800' :
                    source.status === 'inactive' ? 'bg-gray-100 text-gray-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {source.status}
                  </div>
                </div>
                {source.last_update && (
                  <div className="text-xs text-gray-500 mt-2">
                    Last: {formatDate(source.last_update)}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
            <span className="text-red-800">{error}</span>
          </div>
        </div>
      )}
    </div>
  );
};
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
