import React from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, DollarSign, FileText, Users, Calendar } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import SpendChart from '../components/SpendChart';
import RecentInvoices from '../components/RecentInvoices';
import TopVendors from '../components/TopVendors';
import AlertsPanel from '../components/AlertsPanel';

const Dashboard: React.FC = () => {
  const metrics = [
    {
      title: 'Total Legal Spend',
      value: '$2,847,392',
      change: '+12.5%',
      changeType: 'increase' as const,
      icon: DollarSign,
      period: 'vs last quarter'
    },
    {
      title: 'Active Matters',
      value: '156',
      change: '+8',
      changeType: 'increase' as const,
      icon: FileText,
      period: 'this month'
    },
    {
      title: 'Vendor Count',
      value: '47',
      change: '-3',
      changeType: 'decrease' as const,
      icon: Users,
      period: 'active vendors'
    },
    {
      title: 'Avg. Processing Time',
      value: '3.2 days',
      change: '-18%',
      changeType: 'decrease' as const,
      icon: Calendar,
      period: 'invoice processing'
    }
  ];

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Legal Spend Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            Real-time insights into your legal spending and performance metrics
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button className="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200">
            <FileText className="w-4 h-4 mr-2" />
            Generate Report
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <MetricCard key={metric.title} {...metric} index={index} />
        ))}
      </div>

      {/* Charts and Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SpendChart />
        </div>
        <div>
          <AlertsPanel />
        </div>
      </div>

      {/* Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentInvoices />
        <TopVendors />
      </div>
    </div>
  );
};

export default Dashboard;