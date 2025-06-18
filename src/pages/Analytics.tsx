import React, { useState, useEffect } from 'react';
import { BarChart3, PieChart, TrendingUp, Filter, Download, Calendar, AlertTriangle, ChevronLeft } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title } from 'chart.js';
import { Doughnut, Bar, Line } from 'react-chartjs-2';
import { pdfService } from '../services/pdfService';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title);

const Analytics: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [selectedTimeframe, setSelectedTimeframe] = useState('12M');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [aiInsights, setAiInsights] = useState<string[]>([]);

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
      alert('Failed to export analytics report');
    } finally {
      setGenerating(false);
    }
  };

  const spendByCategory = {
    labels: ['Litigation', 'Corporate', 'IP', 'Employment', 'Regulatory', 'M&A'],
    datasets: [
      {
        data: [1200000, 850000, 650000, 420000, 380000, 320000],
        backgroundColor: [
          '#3B82F6',
          '#10B981',
          '#F59E0B',
          '#EF4444',
          '#8B5CF6',
          '#06B6D4',
        ],
        borderWidth: 0,
      },
    ],
  };

  const monthlyTrends = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'External Counsel',
        data: [320000, 290000, 350000, 420000, 380000, 450000, 520000, 480000, 540000, 590000, 620000, 580000],
        backgroundColor: '#3B82F6',
      },
      {
        label: 'Internal Resources',
        data: [100000, 90000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000],
        backgroundColor: '#10B981',
      },
    ],
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 20,
          usePointStyle: true,
        },
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
            const percentage = ((context.raw / total) * 100).toFixed(1);
            return `${context.label}: $${context.raw.toLocaleString()} (${percentage}%)`;
          }
        }
      }
    },
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: $${context.raw.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      x: {
        stacked: true,
      },
      y: {
        stacked: true,
        ticks: {
          callback: function(value: any) {
            return '$' + (value / 1000) + 'K';
          }
        }
      },
    },
  };

  const getTypeLabel = () => {
    switch (type) {
      case 'spend':
        return 'Spend Analytics';
      case 'invoices':
        return 'Invoice Processing Analytics';
      case 'outliers':
        return 'Risk Analysis';
      case 'processing':
        return 'Processing Performance';
      default:
        return 'Legal Spend Analytics';
    }
  };

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
            Deep dive into {type || 'spending'} patterns and trends
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
      
      {/* Key Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Monthly Spend</p>
              <p className="text-2xl font-bold text-gray-900">$542K</p>
            </div>
            <div className="p-3 bg-primary-100 rounded-lg">
              <Calendar className="w-6 h-6 text-primary-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-success-600 font-medium">↑ 8.2%</span>
            <span className="text-sm text-gray-500 ml-2">vs last period</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cost per Matter</p>
              <p className="text-2xl font-bold text-gray-900">$34.2K</p>
            </div>
            <div className="p-3 bg-success-100 rounded-lg">
              <BarChart3 className="w-6 h-6 text-success-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-danger-600 font-medium">↓ 12.5%</span>
            <span className="text-sm text-gray-500 ml-2">vs last period</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Resource Utilization</p>
              <p className="text-2xl font-bold text-gray-900">87%</p>
            </div>
            <div className="p-3 bg-warning-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-warning-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-success-600 font-medium">↑ 5.3%</span>
            <span className="text-sm text-gray-500 ml-2">vs target</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Matter Volume</p>
              <p className="text-2xl font-bold text-gray-900">156</p>
            </div>
            <div className="p-3 bg-info-100 rounded-lg">
              <PieChart className="w-6 h-6 text-info-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-success-600 font-medium">↑ 3.8%</span>
            <span className="text-sm text-gray-500 ml-2">vs last period</span>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Spend by Category</h3>
          <div className="h-80">
            <Doughnut data={spendByCategory} options={doughnutOptions} />
          </div>
        </div>

        {/* Monthly Trends */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Monthly Trends</h3>
          <div className="h-80">
            <Bar data={monthlyTrends} options={barOptions} />
          </div>
        </div>
      </div>

      {/* Type-specific Analytics */}
      {type === 'invoices' && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Invoice Processing Performance</h3>
          {/* Add invoice-specific analytics */}
        </div>
      )}

      {type === 'outliers' && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Analysis Details</h3>
          {/* Add risk analysis details */}
        </div>
      )}

      {type === 'processing' && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Efficiency Metrics</h3>
          {/* Add processing performance metrics */}
        </div>
      )}
    </div>
  );
};

export default Analytics;