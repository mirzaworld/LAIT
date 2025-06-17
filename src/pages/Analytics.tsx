import React, { useState } from 'react';
import { BarChart3, PieChart, TrendingUp, Filter, Download, Calendar } from 'lucide-react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const Analytics: React.FC = () => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('12M');
  const [selectedCategory, setSelectedCategory] = useState('all');

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

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Legal Spend Analytics</h1>
          <p className="mt-1 text-sm text-gray-500">
            Deep dive into spending patterns and trends
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
          <button className="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
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
              <p className="text-sm font-medium text-gray-600">Efficiency Score</p>
              <p className="text-2xl font-bold text-gray-900">87%</p>
            </div>
            <div className="p-3 bg-warning-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-warning-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-success-600 font-medium">↑ 5.3%</span>
            <span className="text-sm text-gray-500 ml-2">vs last period</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Budget Variance</p>
              <p className="text-2xl font-bold text-gray-900">+12%</p>
            </div>
            <div className="p-3 bg-danger-100 rounded-lg">
              <PieChart className="w-6 h-6 text-danger-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-danger-600 font-medium">Over budget</span>
            <span className="text-sm text-gray-500 ml-2">this quarter</span>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Spend by Practice Area</h3>
              <p className="text-sm text-gray-500">Distribution of legal spending</p>
            </div>
          </div>
          <div className="h-80">
            <Doughnut data={spendByCategory} options={doughnutOptions} />
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Monthly Spend Trends</h3>
              <p className="text-sm text-gray-500">External vs internal costs</p>
            </div>
          </div>
          <div className="h-80">
            <Bar data={monthlyTrends} options={barOptions} />
          </div>
        </div>
      </div>

      {/* Performance Insights */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">AI Performance Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="p-4 bg-success-50 rounded-lg border border-success-200">
            <h4 className="font-medium text-success-900 mb-2">Cost Optimization</h4>
            <p className="text-sm text-success-700">
              Switching to alternative counsel for routine matters could save $127K annually
            </p>
          </div>
          <div className="p-4 bg-warning-50 rounded-lg border border-warning-200">
            <h4 className="font-medium text-warning-900 mb-2">Budget Alert</h4>
            <p className="text-sm text-warning-700">
              IP litigation spend is trending 23% above budget for Q4
            </p>
          </div>
          <div className="p-4 bg-primary-50 rounded-lg border border-primary-200">
            <h4 className="font-medium text-primary-900 mb-2">Efficiency Gain</h4>
            <p className="text-sm text-primary-700">
              Document review automation reduced costs by $89K this quarter
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;