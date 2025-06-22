import React, { useState, useEffect } from 'react';
import { BarChart3, PieChart, TrendingUp, Filter, Download, Calendar, AlertTriangle, ChevronLeft, Brain } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { pdfService } from '../services/pdfService';
import LegalAnalytics from '../components/LegalAnalytics';
import MLPoweredAnalytics from '../components/MLPoweredAnalytics';
import ErrorBoundary from '../components/ErrorBoundary';
import SmartButton from '../components/SmartButton';
import '../utils/chartConfig';

const Analytics: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [selectedTimeframe, setSelectedTimeframe] = useState('12M');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [aiInsights, setAiInsights] = useState<string[]>([]);
  const [activeView, setActiveView] = useState<'traditional' | 'ml'>('ml'); // Default to ML view

  const { type = '', dateRange } = location.state || {};

  useEffect(() => {
    setLoading(true);
    // In a real implementation, this would be an API call to the Python backend
    setTimeout(() => {
      setAiInsights([
        "IP litigation spend is trending 23% higher than previous year, primarily driven by TechCorp vs CompetitorX case",
        "Predicted Q3 spend is likely to be 15-20% above budget based on current matter velocity",
        "3 firms account for 62% of total spend; consider diversifying vendor portfolio",
        "Potential savings of $425,000 identified through rate optimization and timekeeper mix adjustments"
      ]);
      setLoading(false);
    }, 1000);
  }, [selectedTimeframe, selectedCategory, type]);

  const handleExport = async () => {
    setGenerating(true);
    try {
      const report = await pdfService.generateReport('current');
      const pdfBlob = await pdfService.generatePDF(report);
      
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `legal_analytics_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting analytics:', err);
    } finally {
      setGenerating(false);
    }
  };

  const getTypeLabel = () => {
    switch(type) {
      case 'spend': return 'Spend Analytics';
      case 'invoices': return 'Invoice Analytics';
      case 'outliers': return 'Outlier Analysis';
      case 'processing': return 'Processing Analytics';
      default: return 'Legal Analytics Dashboard';
    }
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          {type && (
            <SmartButton
              onClick={() => navigate(-1)}
              variant="secondary"
              size="sm"
              className="mb-2"
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Back to Dashboard
            </SmartButton>
          )}
          <h1 className="text-2xl font-bold text-gray-900">{getTypeLabel()}</h1>
          <p className="mt-1 text-sm text-gray-500">
            Deep dive into {type || 'spending'} patterns and trends with AI-powered insights
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
          <SmartButton 
            onClick={handleExport}
            disabled={generating}
            loading={generating}
            variant="primary"
            size="sm"
          >
            <Download className="w-4 h-4 mr-2" />
            Export Analytics
          </SmartButton>
        </div>
      </div>

      {/* View Switcher */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex space-x-1">
            <button
              onClick={() => setActiveView('ml')}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center space-x-2 ${
                activeView === 'ml'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <Brain className="w-4 h-4" />
              <span>ML-Powered Analytics</span>
            </button>
            <button
              onClick={() => setActiveView('traditional')}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center space-x-2 ${
                activeView === 'traditional'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Traditional Analytics</span>
            </button>
          </div>
          <div className="text-sm text-gray-500">
            {activeView === 'ml' ? 'Advanced AI-powered insights and predictions' : 'Standard charts and metrics'}
          </div>
        </div>
      </div>

      {/* ML-Powered Analytics View */}
      {activeView === 'ml' && (
        <ErrorBoundary fallback={({ error }) => (
          <div className="bg-white p-12 rounded-xl shadow-sm border border-gray-200 text-center">
            <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">ML Analytics Unavailable</h3>
            <p className="text-gray-600 mb-4">
              {error?.message || 'ML-powered analytics temporarily unavailable'}
            </p>
            <SmartButton 
              onClick={() => {
                window.location.hash = `#retry-ml-${Date.now()}`;
                setTimeout(() => window.location.hash = '', 100);
              }}
              variant="primary"
            >
              Try Again
            </SmartButton>
          </div>
        )}>
          <MLPoweredAnalytics />
        </ErrorBoundary>
      )}

      {/* Traditional Analytics View */}
      {activeView === 'traditional' && (
        <ErrorBoundary fallback={({ error }) => (
          <div className="bg-white p-12 rounded-xl shadow-sm border border-gray-200 text-center">
            <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Traditional Analytics Unavailable</h3>
            <p className="text-gray-600 mb-4">
              {error?.message || 'Traditional analytics temporarily unavailable'}
            </p>
            <SmartButton 
              onClick={() => {
                window.location.hash = `#retry-traditional-${Date.now()}`;
                setTimeout(() => window.location.hash = '', 100);
              }}
              variant="primary"
            >
              Try Again
            </SmartButton>
          </div>
        )}>
          <div className="space-y-6">
            {/* AI Insights */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">AI-Generated Insights</h2>
                {loading && (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                    <span className="text-sm text-gray-500">Analyzing data...</span>
                  </div>
                )}
              </div>
              <div className="space-y-3">
                {aiInsights.map((insight, index) => (
                  <div 
                    key={index} 
                    className="flex items-start p-3 bg-primary-50 rounded-lg"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <AlertTriangle className="w-5 h-5 text-primary-600 mt-0.5 mr-3 flex-shrink-0" />
                    <p className="text-sm text-gray-800">{insight}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Legal Analytics Component */}
            <LegalAnalytics />
          </div>
        </ErrorBoundary>
      )}
    </div>
  );
};

export default Analytics;
