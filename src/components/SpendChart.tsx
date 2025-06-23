import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Loader2 } from 'lucide-react';
import { useSpendTrends } from '../hooks/useApi';
import { ChartJS, defaultChartOptions } from '../utils/chartConfig';

const SpendChart: React.FC = () => {
  const [period, setPeriod] = useState<string>('monthly');
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(undefined);
  const { trends, loading, error } = useSpendTrends(period, selectedCategory);
  
  // Build the default chart data
  const createChartData = () => {
    if (!trends || !trends.datasets || trends.datasets.length === 0) {
      return {
        labels: [],
        datasets: []
      };
    }
    
    // Get the primary spend dataset (usually the first one)
    const primaryDataset = trends.datasets[0];
    
    // Only show one main trend line
    return {
      labels: trends.labels || [],
      datasets: [
        {
          label: primaryDataset.label || 'Monthly Spend',
          data: primaryDataset.data || [],
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true,
        }
      ]
    };
  };
  
  const getDatasetColor = (index: number, type: 'border' | 'background') => {
    const colors = [
      { border: 'rgb(59, 130, 246)', background: 'rgba(59, 130, 246, 0.1)' },
      { border: 'rgb(34, 197, 94)', background: 'rgba(34, 197, 94, 0.1)' },
      { border: 'rgb(168, 85, 247)', background: 'rgba(168, 85, 247, 0.1)' },
      { border: 'rgb(249, 115, 22)', background: 'rgba(249, 115, 22, 0.1)' }
    ];
    
    const colorSet = colors[index % colors.length];
    return type === 'border' ? colorSet.border : colorSet.background;
  };
  
  const data = createChartData();

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
        },
      },
      title: {
        display: false,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: '#1f2937',
        bodyColor: '#1f2937',
        borderColor: '#e5e7eb',
        borderWidth: 1,
        cornerRadius: 8,
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        border: {
          display: false,
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
        border: {
          display: false,
        },
        ticks: {
          callback: function(value: any) {
            return '$' + (value / 1000) + 'K';
          }
        }
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
  };

  const handlePeriodChange = (newPeriod: string) => {
    setPeriod(newPeriod);
  };
  
  const handleCategoryClick = (category: string | undefined) => {
    // Toggle selected category
    if (category === selectedCategory) {
      setSelectedCategory(undefined);
    } else {
      setSelectedCategory(category);
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Legal Spend Trends</h3>
          <p className="text-sm text-gray-500">Monthly spending analysis and predictions</p>
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={() => handlePeriodChange('monthly')}
            className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
              period === 'monthly' 
                ? 'text-primary-600 bg-primary-50 hover:bg-primary-100' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            12M
          </button>
          <button 
            onClick={() => handlePeriodChange('quarterly')}
            className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
              period === 'quarterly' 
                ? 'text-primary-600 bg-primary-50 hover:bg-primary-100' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Quarterly
          </button>
          <button 
            onClick={() => handlePeriodChange('annually')}
            className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
              period === 'annually' 
                ? 'text-primary-600 bg-primary-50 hover:bg-primary-100' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Yearly
          </button>
        </div>
      </div>
      
      {loading ? (
        <div className="h-80 flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <span className="ml-2 text-gray-500">Loading chart data...</span>
        </div>
      ) : error ? (
        <div className="h-80 flex items-center justify-center bg-danger-50 text-danger-700 rounded-lg">
          <p>Error loading chart data. Please try again.</p>
        </div>
      ) : (
        <>
          <div className="h-80">
            <Line data={data} options={options} />
          </div>
        </>
      )}
    </div>
  );
};

export default SpendChart;