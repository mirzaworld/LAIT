import React, { useState } from 'react';
import { Download, Calendar, Filter, TrendingUp, FileText, PieChart, BarChart3, Zap, RefreshCw } from 'lucide-react';

const Reports: React.FC = () => {
  const [selectedReport, setSelectedReport] = useState('spend-analysis');
  const [dateRange, setDateRange] = useState('last-quarter');
  const [generatingReport, setGeneratingReport] = useState(false);
  const [aiAnalysisActive, setAiAnalysisActive] = useState(false);

  const reportTypes = [
    {
      id: 'spend-analysis',
      name: 'Spend Analysis',
      description: 'Comprehensive spending breakdown by practice area, vendor, and time period',
      icon: PieChart,
      frequency: 'Monthly',
      lastGenerated: '2024-01-15'
    },
    {
      id: 'vendor-performance',
      name: 'Vendor Performance',
      description: 'Performance metrics and cost efficiency analysis for legal vendors',
      icon: TrendingUp,
      frequency: 'Quarterly',
      lastGenerated: '2024-01-10'
    },
    {
      id: 'budget-variance',
      name: 'Budget Variance',
      description: 'Actual vs budgeted spend analysis with variance explanations',
      icon: BarChart3,
      frequency: 'Monthly',
      lastGenerated: '2024-01-12'
    },
    {
      id: 'matter-summary',
      name: 'Matter Summary',
      description: 'Detailed summary of legal matters and associated costs',
      icon: FileText,
      frequency: 'Weekly',
      lastGenerated: '2024-01-14'
    }
  ];

  const savedReports = [
    {
      id: 1,
      name: 'Q4 2024 Legal Spend Analysis',
      type: 'Spend Analysis',
      generated: '2024-01-15',
      size: '2.4 MB',
      format: 'PDF'
    },
    {
      id: 2,
      name: 'Vendor Performance Review - December',
      type: 'Vendor Performance',
      generated: '2024-01-10',
      size: '1.8 MB',
      format: 'Excel'
    },
    {
      id: 3,
      name: 'Budget Variance Report - Q4',
      type: 'Budget Variance',
      generated: '2024-01-12',
      size: '3.1 MB',
      format: 'PDF'
    },
    {
      id: 4,
      name: 'Active Matters Summary',
      type: 'Matter Summary',
      generated: '2024-01-14',
      size: '1.2 MB',
      format: 'Excel'
    }
  ];

  const generateReport = () => {
    // Simulate report generation
    alert(`Generating ${reportTypes.find(r => r.id === selectedReport)?.name} report for ${dateRange}...`);
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="mt-1 text-sm text-gray-500">
            Generate comprehensive reports on legal spending and performance
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button 
            onClick={generateReport}
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200"
          >
            <FileText className="w-4 h-4 mr-2" />
            Generate Report
          </button>
        </div>
      </div>

      {/* AI Report Enhancement Toggle */}
      <div className="bg-primary-50 p-4 rounded-xl border border-primary-200 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary-100 rounded-full">
              <Zap className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">AI-Powered Report Enhancement</h3>
              <p className="text-sm text-gray-600">Enable AI to add predictive analysis, anomaly detection, and optimization recommendations</p>
            </div>
          </div>
          <div className="flex items-center">
            <button 
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 focus:outline-none ${
                aiAnalysisActive ? 'bg-primary-600' : 'bg-gray-200'
              }`}
              onClick={() => setAiAnalysisActive(!aiAnalysisActive)}
            >
              <span 
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${
                  aiAnalysisActive ? 'translate-x-6' : 'translate-x-1'
                }`} 
              />
            </button>
          </div>
        </div>
        
        {aiAnalysisActive && (
          <div className="mt-3 pl-10">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
              <div className="flex items-center space-x-1">
                <CheckCircle className="w-3 h-3 text-success-600" />
                <span>Spend pattern prediction</span>
              </div>
              <div className="flex items-center space-x-1">
                <CheckCircle className="w-3 h-3 text-success-600" />
                <span>Vendor optimization</span>
              </div>
              <div className="flex items-center space-x-1">
                <CheckCircle className="w-3 h-3 text-success-600" />
                <span>Rate benchmarking</span>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Report Configuration */}
        <div className="lg:col-span-2 space-y-6">
          {/* Report Type Selection */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Report Type</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {reportTypes.map((report) => {
                const Icon = report.icon;
                return (
                  <div
                    key={report.id}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
                      selectedReport === report.id
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                    onClick={() => setSelectedReport(report.id)}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`p-2 rounded-lg ${
                        selectedReport === report.id ? 'bg-primary-100' : 'bg-gray-100'
                      }`}>
                        <Icon className={`w-5 h-5 ${
                          selectedReport === report.id ? 'text-primary-600' : 'text-gray-600'
                        }`} />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{report.name}</h4>
                        <p className="text-sm text-gray-600 mt-1">{report.description}</p>
                        <div className="flex items-center justify-between mt-3">
                          <span className="text-xs text-gray-500">{report.frequency}</span>
                          <span className="text-xs text-gray-500">Last: {report.lastGenerated}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Report Configuration */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Report Configuration</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date Range
                </label>
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <select 
                    value={dateRange}
                    onChange={(e) => setDateRange(e.target.value)}
                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="last-week">Last Week</option>
                    <option value="last-month">Last Month</option>
                    <option value="last-quarter">Last Quarter</option>
                    <option value="last-year">Last Year</option>
                    <option value="custom">Custom Range</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Format
                </label>
                <div className="flex items-center space-x-2">
                  <FileText className="w-4 h-4 text-gray-400" />
                  <select className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                    <option value="pdf">PDF Report</option>
                    <option value="excel">Excel Spreadsheet</option>
                    <option value="csv">CSV Data</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filters
              </label>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Filter className="w-4 h-4 text-gray-400" />
                  <select className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                    <option value="all">All Practice Areas</option>
                    <option value="litigation">Litigation</option>
                    <option value="corporate">Corporate</option>
                    <option value="ip">Intellectual Property</option>
                  </select>
                </div>
                <select className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                  <option value="all">All Vendors</option>
                  <option value="top-vendors">Top 10 Vendors</option>
                  <option value="tier1">Tier 1 Firms</option>
                  <option value="boutique">Boutique Firms</option>
                </select>
              </div>
            </div>

            <div className="mt-6 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Estimated generation time: 2-3 minutes
              </div>
              <div className="flex space-x-3">
                <button className="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors duration-200">
                  Preview
                </button>
                <button 
                  onClick={generateReport}
                  className="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200"
                >
                  Generate Report
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Saved Reports */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Recent Reports</h3>
            <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
              View All
            </button>
          </div>
          
          <div className="space-y-4">
            {savedReports.map((report, index) => (
              <div 
                key={report.id}
                className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200 animate-slide-up"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 text-sm">{report.name}</h4>
                    <p className="text-xs text-gray-500 mt-1">{report.type}</p>
                    <div className="flex items-center space-x-4 mt-2">
                      <span className="text-xs text-gray-500">{report.generated}</span>
                      <span className="text-xs text-gray-500">{report.size}</span>
                      <span className="text-xs text-primary-600 font-medium">{report.format}</span>
                    </div>
                  </div>
                  <button className="text-primary-600 hover:text-primary-700 p-1">
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 pt-4 border-t border-gray-200">
            <button className="w-full text-sm text-primary-600 hover:text-primary-700 font-medium text-center">
              View Report Archive
            </button>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Report Statistics</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">247</div>
            <div className="text-sm text-gray-600">Reports Generated</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-success-600">15.6 GB</div>
            <div className="text-sm text-gray-600">Data Analyzed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-warning-600">4.2 min</div>
            <div className="text-sm text-gray-600">Avg Generation Time</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;