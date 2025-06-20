import React, { useState } from 'react';
import { DollarSign, FileText, Users, Calendar, Download, Loader2, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import MetricCard from '../components/MetricCard';
import SpendChart from '../components/SpendChart';
import RecentInvoices from '../components/RecentInvoices';
import TopVendors from '../components/TopVendors';
import AlertsPanel from '../components/AlertsPanel';
import ApiStatus from '../components/ApiStatus';
import { useDashboardMetrics } from '../hooks/useApi';
import { pdfService } from '../services/pdfService';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { metrics: apiMetrics, loading, error } = useDashboardMetrics();
  const [generatingReport, setGeneratingReport] = useState(false);
  const [dateRange, setDateRange] = useState<[Date | null, Date | null]>([null, null]);
  const [startDate, endDate] = dateRange;

  const handleGenerateReport = async () => {
    if (!apiMetrics) return;
    
    setGeneratingReport(true);
    try {
      // Generate report data
      const report = await pdfService.generateReport('current');
      
      // Generate PDF
      const pdfBlob = await pdfService.generatePDF(report);
      
      // Create download link
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `legal_spend_report_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error generating report:', err);
      alert('Failed to generate report. Please try again.');
    } finally {
      setGeneratingReport(false);
    }
  };
  
  const handleDateChange = (update: [Date | null, Date | null]) => {
    setDateRange(update);
    // Trigger analytics update based on date range
    console.log('Fetching analytics for:', update);
  };

  const handleViewAnalytics = (metricType: string) => {
    switch (metricType) {
      case 'spend':
        navigate('/analytics/spend', {
          state: { dateRange, type: 'spend' }
        });
        break;
      case 'invoices':
        navigate('/analytics/invoices', {
          state: { dateRange, type: 'invoices' }
        });
        break;
      case 'outliers':
        navigate('/analytics/risks', {
          state: { dateRange, type: 'outliers' }
        });
        break;
      case 'processing':
        navigate('/analytics/processing', {
          state: { dateRange, type: 'processing' }
        });
        break;
      default:
        navigate('/analytics');
    }
  };

  const metrics = [
    {
      title: 'Total Spend',
      value: apiMetrics ? `$${apiMetrics.total_spend.toLocaleString()}` : '$0',
      change: apiMetrics ? `${apiMetrics.spend_change_percentage >= 0 ? '+' : ''}${apiMetrics.spend_change_percentage.toFixed(1)}%` : '+0%',
      changeType: (apiMetrics && apiMetrics.spend_change_percentage >= 0 ? 'increase' : 'decrease') as 'increase' | 'decrease',
      icon: DollarSign,
      period: 'vs last period',
      onClick: () => handleViewAnalytics('spend')
    },
    {
      title: 'Invoices Processed',
      value: apiMetrics ? apiMetrics.invoice_count.toString() : '0',
      change: '+8',
      changeType: 'increase' as const,
      icon: FileText,
      period: 'this month',
      onClick: () => handleViewAnalytics('invoices')
    },
    {
      title: 'High Risk Flags',
      value: apiMetrics ? apiMetrics.high_risk_invoices_count.toString() : '0',
      change: apiMetrics ? `${apiMetrics.risk_factors_count}` : '0',
      changeType: 'decrease' as const,
      icon: AlertTriangle,
      period: 'total risk factors',
      onClick: () => handleViewAnalytics('outliers')
    },
    {
      title: 'Avg Processing Time',
      value: apiMetrics ? `${apiMetrics.avg_processing_time.toFixed(1)} days` : '0 days',
      change: '-18%',
      changeType: 'decrease' as const,
      icon: Calendar,
      period: 'invoice processing',
      onClick: () => handleViewAnalytics('processing')
    }
  ];

  const spendTrendData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Spend ($)',
        data: [12000, 15000, 18000, 20000, 22000, 25000],
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
      },
    ],
  };

  const outlierRateData = {
    datasets: [
      {
        data: [5, 95],
        backgroundColor: ['rgba(220, 38, 38, 1)', 'rgba(229, 231, 235, 1)'],
        borderWidth: 0,
      },
    ],
  };

  const outlierRate = 5;

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
          <button 
            onClick={handleGenerateReport}
            disabled={generatingReport || loading}
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {generatingReport ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                Generate Report
              </>
            )}
          </button>
        </div>
      </div>

      {/* Date Range Picker */}
      <div className="flex items-center space-x-4">
        <DatePicker
          selectsRange
          startDate={startDate}
          endDate={endDate}
          onChange={handleDateChange}
          className="border border-gray-300 rounded-lg py-2 px-3 shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          placeholderText="Select date range"
        />
      </div>

      {/* Metrics Grid */}
      {loading ? (
        <div className="h-48 flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <span className="ml-2 text-gray-500">Loading metrics...</span>
        </div>
      ) : error ? (
        <div className="h-48 flex items-center justify-center bg-danger-50 text-danger-700 rounded-lg">
          <p>Error loading metrics. Please try again.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric, index) => (
            <MetricCard key={metric.title} {...metric} index={index} />
          ))}
        </div>
      )}

      {/* Charts and Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SpendChart />
          <div className="lg:col-span-2">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Spend Trend</h3>
            <Line data={spendTrendData} options={{ responsive: true, plugins: { legend: { position: 'top' } } }} />
          </div>
        </div>
        <div>
          <AlertsPanel />
        </div>
      </div>

      {/* Outlier Rate Gauge */}
      <div className="bg-white p-6 rounded-xl shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Outlier Rate</h3>
        <div className="w-32 h-32 mx-auto">
          <CircularProgressbar
            value={outlierRate}
            maxValue={100}
            text={`${outlierRate}%`}
            styles={buildStyles({
              textColor: '#dc2626',
              pathColor: '#dc2626',
              trailColor: '#e5e7eb',
            })}
          />
        </div>
      </div>

      {/* Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentInvoices />
        <TopVendors />
      </div>

      {/* View Details Button */}
      <div className="flex justify-center mt-8">
        <button
          onClick={() => navigate('/analytics')}
          className="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200"
        >
          View Full Analytics
        </button>
      </div>
      
      {/* API Status Display */}
      <div className="flex justify-center mt-6">
        <div className="flex flex-wrap gap-3 justify-center">
          <ApiStatus url="/api/health" label="API Status" />
          <ApiStatus url="/api/ml/test" label="ML Service" />
          <ApiStatus url="/api/workflow/electronic-billing" label="Workflow" />
          <button 
            onClick={() => navigate('/diagnostics')}
            className="text-sm text-blue-600 hover:underline"
          >
            View diagnostics
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;