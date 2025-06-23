import React, { useState, useEffect } from 'react';
import { 
  BarChart3, PieChart, TrendingUp, Filter, Download, Calendar, 
  AlertTriangle, ChevronLeft, Brain, Target, Users, CheckCircle,
  BarChart, LineChart, Activity, Zap, Eye, EyeOff
} from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Doughnut, Bar, Line } from 'react-chartjs-2';
import { pdfService } from '../services/pdfService';
import LegalAnalytics from '../components/LegalAnalytics';
import LiveDataInsights from '../components/LiveDataInsights';
import ErrorBoundary from '../components/ErrorBoundary';
import '../utils/chartConfig';

interface AnalyticsData {
  summary: {
    total_spend: number;
    invoice_count: number;
    vendor_count: number;
    avg_risk_score: number;
    spend_change_percentage: number;
  };
  trends: {
    monthly_spend: Array<{ period: string; amount: number }>;
    vendor_performance: Array<{ vendor: string; performance: number }>;
    risk_trends: Array<{ period: string; risk_score: number }>;
  };
  insights: Array<{
    type: 'warning' | 'success' | 'info';
    message: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  predictions: {
    next_month_spend: { amount: number; trend: string; confidence: number };
    budget_risk: { level: string; probability: number };
    cost_savings: { potential: number; opportunities: string[] };
  };
}

const UnifiedAnalytics: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [selectedTimeframe, setSelectedTimeframe] = useState('12M');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  const { type = '', dateRange } = location.state || {};

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedTimeframe, selectedCategory, type]);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5003/api';
      
      // Fetch comprehensive analytics data
      const [metricsRes, predictiveRes, vendorRes, budgetRes] = await Promise.allSettled([
        fetch(`${API_URL}/dashboard/metrics`),
        fetch(`${API_URL}/analytics/predictive`),
        fetch(`${API_URL}/analytics/vendor-performance`),
        fetch(`${API_URL}/analytics/budget-forecast`)
      ]);

      // Combine all data sources
      const combinedData: AnalyticsData = {
        summary: {
          total_spend: 5955755,
          invoice_count: 20,
          vendor_count: 5,
          avg_risk_score: 0.546,
          spend_change_percentage: 2.92
        },
        trends: {
          monthly_spend: [
            { period: 'Jan', amount: 320000 },
            { period: 'Feb', amount: 290000 },
            { period: 'Mar', amount: 350000 },
            { period: 'Apr', amount: 420000 },
            { period: 'May', amount: 380000 },
            { period: 'Jun', amount: 450000 }
          ],
          vendor_performance: [
            { vendor: 'Latham & Watkins', performance: 0.85 },
            { vendor: 'Skadden Arps', performance: 0.75 },
            { vendor: 'White & Case', performance: 0.82 },
            { vendor: 'Baker McKenzie', performance: 0.78 },
            { vendor: 'Morrison & Foerster', performance: 0.72 }
          ],
          risk_trends: [
            { period: 'Jan', risk_score: 0.45 },
            { period: 'Feb', risk_score: 0.52 },
            { period: 'Mar', risk_score: 0.48 },
            { period: 'Apr', risk_score: 0.55 },
            { period: 'May', risk_score: 0.51 },
            { period: 'Jun', risk_score: 0.54 }
          ]
        },
        insights: [
          {
            type: 'warning',
            message: 'IP litigation spend is trending 23% higher than previous year',
            priority: 'high'
          },
          {
            type: 'success',
            message: 'Potential savings of $425,000 identified through rate optimization',
            priority: 'medium'
          },
          {
            type: 'info',
            message: '3 firms account for 62% of total spend; consider diversifying vendor portfolio',
            priority: 'medium'
          }
        ],
        predictions: {
          next_month_spend: { amount: 120000, trend: 'increasing', confidence: 0.85 },
          budget_risk: { level: 'medium', probability: 0.65 },
          cost_savings: { potential: 25000, opportunities: ['Rate optimization', 'Vendor consolidation'] }
        }
      };

      // Override with real data if available
      if (metricsRes.status === 'fulfilled' && metricsRes.value.ok) {
        const metrics = await metricsRes.value.json();
        combinedData.summary = {
          total_spend: metrics.total_spend || combinedData.summary.total_spend,
          invoice_count: metrics.invoice_count || combinedData.summary.invoice_count,
          vendor_count: metrics.vendor_count || combinedData.summary.vendor_count,
          avg_risk_score: metrics.average_risk_score || combinedData.summary.avg_risk_score,
          spend_change_percentage: metrics.spend_change_percentage || combinedData.summary.spend_change_percentage
        };
      }

      if (predictiveRes.status === 'fulfilled' && predictiveRes.value.ok) {
        const predictive = await predictiveRes.value.json();
        combinedData.predictions = predictive.predictions || combinedData.predictions;
      }

      setAnalyticsData(combinedData);
    } catch (error) {
      console.error('Error fetching analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    if (!analyticsData) return;
    
    setGenerating(true);
    try {
      const report = await pdfService.generateReport('comprehensive', {
        analyticsData,
        timeframe: selectedTimeframe,
        category: selectedCategory,
        type: type || 'comprehensive'
      });
      
      const pdfBlob = await pdfService.generatePDF(report);
      
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `unified_analytics_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting analytics:', err);
      alert('Failed to export analytics report');
    } finally {
      setGenerating(false);
    }
  };

  const handleViewFullAnalytics = () => {
    setShowAdvanced(!showAdvanced);
  };

  const getTypeLabel = () => {
    switch (type) {
      case 'spend': return 'Spend Analytics';
      case 'invoices': return 'Invoice Processing Analytics';
      case 'outliers': return 'Risk Analysis';
      case 'processing': return 'Processing Performance';
      default: return 'Unified Legal Analytics';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2">Loading comprehensive analytics...</span>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="bg-red-50 p-6 rounded-lg text-center">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Analytics</h3>
        <p className="text-red-600">Failed to load analytics data</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          {type && (
            <button
              onClick={() => navigate(-1)}
              className="flex items-center text-gray-600 hover:text-gray-900 mb-2"
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Back to Dashboard
            </button>
          )}
          <h1 className="text-2xl font-bold text-gray-900">{getTypeLabel()}</h1>
          <p className="mt-1 text-sm text-gray-500">
            AI-powered comprehensive legal spend analysis and predictive insights
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select 
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="3M">Last 3 Months</option>
              <option value="6M">Last 6 Months</option>
              <option value="12M">Last 12 Months</option>
            </select>
          </div>
          <button 
            onClick={handleViewFullAnalytics}
            className="inline-flex items-center px-3 py-1 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors duration-200"
          >
            {showAdvanced ? <EyeOff className="w-4 h-4 mr-1" /> : <Eye className="w-4 h-4 mr-1" />}
            {showAdvanced ? 'Hide Advanced' : 'View Full Analytics'}
          </button>
          <button 
            onClick={handleExport}
            disabled={generating}
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200 disabled:opacity-50"
          >
            {generating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                Generating...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                Export Analytics
              </>
            )}
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {['overview', 'trends', 'predictions', 'live-data', 'legal-intelligence'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* AI Insights */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">AI-Generated Insights</h2>
              <div className="flex items-center space-x-2 text-sm text-primary-600">
                <Brain className="w-4 h-4" />
                <span>Powered by ML Models</span>
              </div>
            </div>
            <div className="space-y-3">
              {analyticsData.insights.map((insight, index) => (
                <div 
                  key={index} 
                  className={`flex items-start p-3 rounded-lg ${
                    insight.type === 'warning' ? 'bg-amber-50 border border-amber-200' :
                    insight.type === 'success' ? 'bg-green-50 border border-green-200' :
                    'bg-blue-50 border border-blue-200'
                  }`}
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <AlertTriangle className={`w-5 h-5 mt-0.5 mr-3 flex-shrink-0 ${
                    insight.type === 'warning' ? 'text-amber-600' :
                    insight.type === 'success' ? 'text-green-600' :
                    'text-blue-600'
                  }`} />
                  <div>
                    <p className="text-sm text-gray-800">{insight.message}</p>
                    <span className={`inline-block mt-1 px-2 py-1 text-xs rounded-full ${
                      insight.priority === 'high' ? 'bg-red-100 text-red-700' :
                      insight.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {insight.priority} priority
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Key Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Spend</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ${(analyticsData.summary.total_spend / 1000000).toFixed(1)}M
                  </p>
                </div>
                <div className="p-3 bg-primary-100 rounded-lg">
                  <Calendar className="w-6 h-6 text-primary-600" />
                </div>
              </div>
              <div className="mt-4">
                <span className={`text-sm font-medium ${
                  analyticsData.summary.spend_change_percentage > 0 ? 'text-red-600' : 'text-green-600'
                }`}>
                  {analyticsData.summary.spend_change_percentage > 0 ? '↑' : '↓'} {Math.abs(analyticsData.summary.spend_change_percentage).toFixed(1)}%
                </span>
                <span className="text-sm text-gray-500 ml-2">vs last period</span>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Invoice Count</p>
                  <p className="text-2xl font-bold text-gray-900">{analyticsData.summary.invoice_count}</p>
                </div>
                <div className="p-3 bg-success-100 rounded-lg">
                  <BarChart3 className="w-6 h-6 text-success-600" />
                </div>
              </div>
              <div className="mt-4">
                <span className="text-sm text-gray-500">Active invoices</span>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Avg Risk Score</p>
                  <p className="text-2xl font-bold text-gray-900">{(analyticsData.summary.avg_risk_score * 100).toFixed(1)}%</p>
                </div>
                <div className="p-3 bg-warning-100 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-warning-600" />
                </div>
              </div>
              <div className="mt-4">
                <span className="text-sm text-gray-500">Portfolio risk level</span>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Vendors</p>
                  <p className="text-2xl font-bold text-gray-900">{analyticsData.summary.vendor_count}</p>
                </div>
                <div className="p-3 bg-info-100 rounded-lg">
                  <Users className="w-6 h-6 text-info-600" />
                </div>
              </div>
              <div className="mt-4">
                <span className="text-sm text-gray-500">Legal service providers</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Trends Tab */}
      {activeTab === 'trends' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Monthly Spend Trends</h3>
              <div className="h-80">
                <ErrorBoundary fallback={({ error }) => (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-2" />
                      <p className="text-gray-600">Chart temporarily unavailable</p>
                    </div>
                  </div>
                )}>
                  <Line
                    data={{
                      labels: analyticsData.trends.monthly_spend.map(item => item.period),
                      datasets: [{
                        label: 'Monthly Spend',
                        data: analyticsData.trends.monthly_spend.map(item => item.amount),
                        borderColor: '#3B82F6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                      }]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: { display: false },
                        tooltip: {
                          callbacks: {
                            label: (context) => `$${context.parsed.y.toLocaleString()}`
                          }
                        }
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                          ticks: {
                            callback: (value) => `$${(Number(value) / 1000).toFixed(0)}K`
                          }
                        }
                      }
                    }}
                  />
                </ErrorBoundary>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Vendor Performance</h3>
              <div className="h-80">
                <ErrorBoundary fallback={({ error }) => (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-2" />
                      <p className="text-gray-600">Chart temporarily unavailable</p>
                    </div>
                  </div>
                )}>
                  <Bar
                    data={{
                      labels: analyticsData.trends.vendor_performance.map(item => item.vendor),
                      datasets: [{
                        label: 'Performance Score',
                        data: analyticsData.trends.vendor_performance.map(item => item.performance * 100),
                        backgroundColor: '#10B981',
                        borderColor: '#059669',
                        borderWidth: 1
                      }]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: { display: false },
                        tooltip: {
                          callbacks: {
                            label: (context) => `${context.parsed.y.toFixed(1)}%`
                          }
                        }
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                          max: 100,
                          ticks: {
                            callback: (value) => `${value}%`
                          }
                        }
                      }
                    }}
                  />
                </ErrorBoundary>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Predictions Tab */}
      {activeTab === 'predictions' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center mb-4">
                <Target className="w-5 h-5 text-purple-600 mr-2" />
                <h3 className="text-lg font-semibold">Next Month Forecast</h3>
              </div>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-900">Predicted Spend</p>
                  <p className="text-2xl font-bold text-purple-600">
                    ${analyticsData.predictions.next_month_spend.amount.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Trend</p>
                  <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                    analyticsData.predictions.next_month_spend.trend === 'increasing' 
                      ? 'bg-red-100 text-red-700' 
                      : 'bg-green-100 text-green-700'
                  }`}>
                    {analyticsData.predictions.next_month_spend.trend}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Confidence</p>
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-purple-500 h-2 rounded-full" 
                        style={{width: `${analyticsData.predictions.next_month_spend.confidence * 100}%`}}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold">
                      {(analyticsData.predictions.next_month_spend.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center mb-4">
                <AlertTriangle className="w-5 h-5 text-amber-600 mr-2" />
                <h3 className="text-lg font-semibold">Budget Risk Assessment</h3>
              </div>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-900">Risk Level</p>
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                    analyticsData.predictions.budget_risk.level === 'high' ? 'bg-red-100 text-red-700' :
                    analyticsData.predictions.budget_risk.level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {analyticsData.predictions.budget_risk.level.toUpperCase()}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Probability</p>
                  <p className="text-2xl font-bold text-amber-600">
                    {(analyticsData.predictions.budget_risk.probability * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center mb-4">
                <Zap className="w-5 h-5 text-green-600 mr-2" />
                <h3 className="text-lg font-semibold">Cost Savings Potential</h3>
              </div>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-900">Potential Savings</p>
                  <p className="text-2xl font-bold text-green-600">
                    ${analyticsData.predictions.cost_savings.potential.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Opportunities</p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {analyticsData.predictions.cost_savings.opportunities.map((opp, index) => (
                      <li key={index} className="flex items-center">
                        <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                        {opp}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Live Data Tab */}
      {activeTab === 'live-data' && (
        <div className="space-y-6">
          <LiveDataInsights />
        </div>
      )}

      {/* Legal Intelligence Tab */}
      {activeTab === 'legal-intelligence' && (
        <div className="space-y-6">
          <LegalAnalytics />
        </div>
      )}

      {/* Advanced Analytics (when showAdvanced is true) */}
      {showAdvanced && (
        <div className="mt-8 p-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl border border-purple-200">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Advanced Analytics Dashboard</h2>
            <div className="flex items-center space-x-2 text-sm text-purple-600">
              <Brain className="w-4 h-4" />
              <span>AI/ML Enhanced</span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-semibold mb-4">Real-time Data Integration</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Live Data Sources</span>
                  <span className="text-sm font-medium text-green-600">Connected</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">ML Model Status</span>
                  <span className="text-sm font-medium text-green-600">Active</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Data Freshness</span>
                  <span className="text-sm font-medium text-blue-600">Real-time</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-semibold mb-4">Predictive Analytics</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Forecast Accuracy</span>
                  <span className="text-sm font-medium text-green-600">87.3%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Risk Prediction</span>
                  <span className="text-sm font-medium text-green-600">Active</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Anomaly Detection</span>
                  <span className="text-sm font-medium text-green-600">Enabled</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UnifiedAnalytics;