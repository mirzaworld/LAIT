import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line
} from 'recharts';
import { AlertTriangle, ArrowUpRight, Loader2 } from 'lucide-react';

interface VendorAnalysisProps {
  vendorId?: string;
  vendorName?: string;
}

const VendorAnalysis: React.FC<VendorAnalysisProps> = ({ vendorId, vendorName = 'All Vendors' }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'1m' | '3m' | '6m' | '1y' | 'all'>('6m');
  
  const timeframeOptions = [
    { value: '1m', label: '1 Month' },
    { value: '3m', label: '3 Months' },
    { value: '6m', label: '6 Months' },
    { value: '1y', label: '1 Year' },
    { value: 'all', label: 'All Time' }
  ];
  
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  useEffect(() => {
    const fetchVendorAnalysis = async () => {
      setLoading(true);
      setError(null);
      
      try {
        let url = `/api/analytics/vendors`;
        
        if (vendorId) {
          url += `/${vendorId}`;
        }
        
        url += `?timeframe=${selectedTimeframe}`;
        
        const response = await fetch(url, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('lait_token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch vendor analysis');
        console.error('Error fetching vendor analysis:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchVendorAnalysis();
  }, [vendorId, selectedTimeframe]);
  
  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
        <span className="ml-2">Loading vendor analysis...</span>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 p-4">
        <div className="flex">
          <AlertTriangle className="h-6 w-6 text-red-500" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error loading vendor analysis</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <p className="text-sm text-red-700 mt-2">Try refreshing the page or contact support if the problem persists.</p>
          </div>
        </div>
      </div>
    );
  }
  
  // If no data available yet, show placeholder with mock data
  if (!data) {
    return (
      <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
        <div className="flex">
          <AlertTriangle className="h-6 w-6 text-blue-500" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">No data available</h3>
            <p className="text-sm text-blue-700 mt-1">
              There is no analysis data available for {vendorName} in the selected time period.
            </p>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-900">{vendorName} Analysis</h2>
        <div className="flex space-x-2">
          {timeframeOptions.map(option => (
            <button
              key={option.value}
              className={`px-3 py-1 text-sm rounded-md ${
                selectedTimeframe === option.value 
                ? 'bg-primary-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              onClick={() => setSelectedTimeframe(option.value as any)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
      
      {/* Spend over time */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium mb-4">Spend Over Time</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data.spendOverTime}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="amount" 
                stroke="#2563EB" 
                activeDot={{ r: 8 }} 
                name="Spend"
              />
              {data.benchmark && (
                <Line 
                  type="monotone" 
                  dataKey="benchmark" 
                  stroke="#9333EA" 
                  strokeDasharray="5 5" 
                  name="Industry Benchmark"
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Category distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-4">Spend by Category</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.categories}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {data.categories.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Performance metrics */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-4">Performance Metrics</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={data.performanceMetrics}
                margin={{ top: 20, right: 30, left: 60, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 100]} />
                <YAxis dataKey="name" type="category" />
                <Tooltip formatter={(value) => `${value}%`} />
                <Bar dataKey="value" fill="#3B82F6" name="Performance Score" />
                {data.benchmarkMetrics && (
                  <Bar dataKey="benchmark" fill="#9CA3AF" name="Industry Average" />
                )}
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* Key insights */}
      {data.insights && data.insights.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-4">Key Insights</h3>
          <ul className="space-y-3">
            {data.insights.map((insight: string, index: number) => (
              <li key={index} className="flex items-start">
                <ArrowUpRight className="h-5 w-5 text-primary-600 mr-2 mt-0.5 flex-shrink-0" />
                <span>{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <div className="bg-green-50 p-6 rounded-lg border border-green-100">
          <h3 className="text-lg font-medium text-green-800 mb-4">Recommendations</h3>
          <ul className="space-y-3">
            {data.recommendations.map((recommendation: string, index: number) => (
              <li key={index} className="flex items-start">
                <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-green-200 text-green-800 mr-2 flex-shrink-0">
                  {index + 1}
                </span>
                <span className="text-green-900">{recommendation}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default VendorAnalysis;
