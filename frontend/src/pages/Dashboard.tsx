import React, { useEffect, useState } from 'react';
import { DollarSign, FileText, Users, TrendingUp, AlertCircle, Loader2 } from 'lucide-react';
import api from '../../../src/services/api';

interface AnalyticsSummary {
  total_invoices: number;
  total_amount: number;
  total_vendors: number;
  monthly_spending: number;
  top_vendors: Array<{
    name: string;
    amount: number;
    count: number;
  }>;
  recent_invoices: Array<{
    id: string;
    vendor: string;
    amount: number;
    date: string;
    status: string;
  }>;
  spending_by_month: Array<{
    month: string;
    amount: number;
  }>;
}

interface KPICardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
}

const KPICard: React.FC<KPICardProps> = ({ title, value, icon, change, changeType = 'neutral' }) => {
  const changeColorClass = {
    positive: 'text-green-600',
    negative: 'text-red-600',
    neutral: 'text-gray-600',
  }[changeType];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          {change && (
            <p className={`text-sm mt-2 flex items-center ${changeColorClass}`}>
              <TrendingUp className="h-4 w-4 mr-1" />
              {change}
            </p>
          )}
        </div>
        <div className="p-3 bg-blue-50 rounded-lg">
          {icon}
        </div>
      </div>
    </div>
  );
};

const SimpleAreaChart: React.FC<{ data: Array<{ month: string; amount: number }> }> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500">
        No spending data available
      </div>
    );
  }

  const maxAmount = Math.max(...data.map(d => d.amount));
  const minAmount = Math.min(...data.map(d => d.amount));
  const range = maxAmount - minAmount || 1;

  return (
    <div className="h-64 relative bg-gradient-to-b from-blue-50 to-white rounded-lg p-4">
      <div className="flex items-end justify-between h-full space-x-2">
        {data.map((point, index) => {
          const height = ((point.amount - minAmount) / range) * 80 + 10;
          return (
            <div key={index} className="flex-1 flex flex-col items-center">
              <div className="relative flex-1 w-full flex items-end">
                <div
                  className="w-full bg-gradient-to-t from-blue-500 to-blue-300 rounded-t-sm transition-all duration-500 hover:from-blue-600 hover:to-blue-400 cursor-pointer"
                  style={{ height: `${height}%` }}
                  title={`${point.month}: $${point.amount.toLocaleString()}`}
                />
              </div>
              <div className="mt-2 text-xs text-gray-600 transform rotate-45 origin-left">
                {point.month.slice(0, 3)}
              </div>
            </div>
          );
        })}
      </div>
      <div className="absolute top-2 right-2 text-xs text-gray-500">
        Peak: ${maxAmount.toLocaleString()}
      </div>
    </div>
  );
};

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('📊 Fetching analytics summary...');
        
        const data = await api.analytics.summary();
        console.log('✅ Analytics summary received:', data);
        setSummary(data);
      } catch (err: any) {
        console.error('❌ Failed to fetch analytics summary:', err);
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-sm border border-red-200 p-6 max-w-md">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Dashboard Error</h2>
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">No data available</p>
      </div>
    );
  }

  // Calculate month-over-month change for spending
  const getMonthlyChange = (): string => {
    if (!summary.spending_by_month || summary.spending_by_month.length < 2) {
      return '';
    }
    const currentMonth = summary.spending_by_month[summary.spending_by_month.length - 1];
    const previousMonth = summary.spending_by_month[summary.spending_by_month.length - 2];
    const change = ((currentMonth.amount - previousMonth.amount) / previousMonth.amount) * 100;
    return `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Legal Spending Dashboard</h1>
          <p className="text-gray-600 mt-2">Monitor your legal spend, invoices, and vendor relationships</p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <KPICard
            title="Total Spend"
            value={`$${summary.total_amount.toLocaleString()}`}
            icon={<DollarSign className="h-6 w-6 text-blue-600" />}
            change={getMonthlyChange()}
            changeType={getMonthlyChange().startsWith('+') ? 'negative' : 'positive'}
          />
          <KPICard
            title="Total Invoices"
            value={summary.total_invoices.toString()}
            icon={<FileText className="h-6 w-6 text-blue-600" />}
            change={`${summary.recent_invoices.length} recent`}
            changeType="neutral"
          />
          <KPICard
            title="Active Vendors"
            value={summary.total_vendors.toString()}
            icon={<Users className="h-6 w-6 text-blue-600" />}
            change={`${summary.top_vendors.length} top performers`}
            changeType="neutral"
          />
        </div>

        {/* Charts and Data Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Spending Trend Chart */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Spending Trend</h3>
              <TrendingUp className="h-5 w-5 text-gray-400" />
            </div>
            <SimpleAreaChart data={summary.spending_by_month} />
          </div>

          {/* Top Vendors */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Top Vendors</h3>
            <div className="space-y-4">
              {summary.top_vendors.slice(0, 5).map((vendor, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mr-3" />
                    <span className="font-medium text-gray-900">{vendor.name}</span>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900">
                      ${vendor.amount.toLocaleString()}
                    </div>
                    <div className="text-xs text-gray-500">
                      {vendor.count} invoice{vendor.count !== 1 ? 's' : ''}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Invoices */}
        <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Recent Invoices</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Invoice ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vendor
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {summary.recent_invoices.slice(0, 10).map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {invoice.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {invoice.vendor}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                      ${invoice.amount.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(invoice.date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        invoice.status === 'processed' 
                          ? 'bg-green-100 text-green-800'
                          : invoice.status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {invoice.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
