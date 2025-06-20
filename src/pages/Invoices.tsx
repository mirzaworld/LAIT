import React, { useState, useEffect } from 'react';
import { Upload, Search, Filter, Download, Eye, CheckCircle, XCircle, Clock, AlertTriangle, AlertCircle, Zap } from 'lucide-react';
import { useInvoices } from '../hooks/useApi';
import { Invoice } from '../services/api';

const Invoices: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedInvoices, setSelectedInvoices] = useState<string[]>([]);
  const [selectedInvoice, setSelectedInvoice] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  // Use API hook instead of hardcoded data
  const { invoices, loading, error, refetch } = useInvoices(
    statusFilter !== 'all' ? statusFilter : undefined
  );

  // Filter invoices based on search term
  const filteredInvoices = invoices.filter(invoice =>
    invoice.vendor.toLowerCase().includes(searchTerm.toLowerCase()) ||
    invoice.matter.toLowerCase().includes(searchTerm.toLowerCase()) ||
    invoice.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-4 h-4 text-success-500" />;
      case 'flagged':
        return <AlertTriangle className="w-4 h-4 text-danger-500" />;
      case 'rejected':
        return <XCircle className="w-4 h-4 text-danger-500" />;
      case 'pending':
      case 'processing':
        return <Clock className="w-4 h-4 text-warning-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = "px-2 py-1 text-xs font-medium rounded-full";
    switch (status) {
      case 'approved':
        return `${baseClasses} bg-success-100 text-success-700`;
      case 'flagged':
        return `${baseClasses} bg-danger-100 text-danger-700`;
      case 'rejected':
        return `${baseClasses} bg-danger-100 text-danger-700`;
      case 'pending':
        return `${baseClasses} bg-warning-100 text-warning-700`;
      case 'processing':
        return `${baseClasses} bg-primary-100 text-primary-700`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-700`;
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 70) return 'text-danger-600 bg-danger-100';
    if (score >= 40) return 'text-warning-600 bg-warning-100';
    return 'text-success-600 bg-success-100';
  };

  const toggleInvoiceSelection = (invoiceId: string) => {
    setSelectedInvoices(prev => 
      prev.includes(invoiceId) 
        ? prev.filter(id => id !== invoiceId)
        : [...prev, invoiceId]
    );
  };

  const selectAllInvoices = () => {
    if (selectedInvoices.length === filteredInvoices.length) {
      setSelectedInvoices([]);
    } else {
      setSelectedInvoices(filteredInvoices.map(inv => inv.id));
    }
  };
  
  const analyzeInvoice = (invoiceId: string) => {
    // Find the invoice
    const invoice = invoices.find(inv => inv.id === invoiceId);
    if (!invoice) return;
    
    // Set selected invoice and start analysis
    setSelectedInvoice(invoiceId);
    setIsAnalyzing(true);
    
    // In a real implementation, this would call the backend API
    setTimeout(() => {
      // Mock analysis result from AI model
      const result = {
        invoice_id: invoice.id,
        risk_score: invoice.riskScore,
        risk_level: invoice.riskScore >= 70 ? 'high' : invoice.riskScore >= 40 ? 'medium' : 'low',
        anomalies: invoice.riskScore >= 70 ? [
          {
            type: 'Unusual Rate Increase',
            message: '340% increase from previous billing period indicates potential oversight or error'
          },
          {
            type: 'Block Billing',
            message: 'Multiple distinct tasks combined in single time entries'
          }
        ] : invoice.riskScore >= 40 ? [
          {
            type: 'Timekeeper Mix',
            message: 'Partner heavy staffing (65% of hours) on routine matter'
          }
        ] : [],
        recommendations: invoice.riskScore >= 70 ? 
          ['Request detailed timekeeper breakdown', 'Compare to benchmark rates', 'Consider negotiation'] :
          invoice.riskScore >= 40 ?
          ['Review staffing allocation', 'Approve with staffing comment'] :
          ['Approve for payment']
      };
      
      setAnalysisResult(result);
      setIsAnalyzing(false);
    }, 1500);
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-500">Loading invoices...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-danger-50 text-danger-700 p-4 rounded-lg flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2" />
          <div>
            <p className="font-medium">Error loading invoices</p>
            <p className="text-sm">{error}</p>
            <button 
              onClick={refetch}
              className="mt-2 text-sm underline hover:no-underline"
            >
              Try again
            </button>
          </div>
        </div>
      )}

      {/* Main Content - Only show when not loading and no error */}
      {!loading && !error && (
        <>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Invoice Management</h1>
          <p className="mt-1 text-sm text-gray-500">
            Review, analyze, and approve legal invoices
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-3">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors duration-200">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
          <button className="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200">
            <Upload className="w-4 h-4 mr-2" />
            Upload Invoice
          </button>
        </div>
      </div>

      {/* Upload Area */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 border-dashed">
        <div className="text-center">
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <div className="mt-4">
            <p className="text-lg font-medium text-gray-900">Upload invoices for AI analysis</p>
            <p className="text-sm text-gray-500 mt-1">
              Drag and drop your PDF invoices or click to browse
            </p>
          </div>
          <div className="mt-6">
            <button className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700">
              Select Files
            </button>
          </div>
        </div>
      </div>
      
      {/* AI Analysis Panel */}
      {analysisResult && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">AI Invoice Analysis</h2>
            <button 
              onClick={() => setAnalysisResult(null)}
              className="text-gray-400 hover:text-gray-500"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>
          
          <div className="mb-4 flex items-center space-x-3">
            <div className={`p-2 rounded-full ${
              analysisResult.risk_level === 'high' ? 'bg-danger-100' : 
              analysisResult.risk_level === 'medium' ? 'bg-warning-100' : 
              'bg-success-100'
            }`}>
              {analysisResult.risk_level === 'high' ? 
                <AlertTriangle className="w-6 h-6 text-danger-600" /> :
                analysisResult.risk_level === 'medium' ? 
                <AlertCircle className="w-6 h-6 text-warning-600" /> :
                <CheckCircle className="w-6 h-6 text-success-600" />
              }
            </div>
            <div>
              <h3 className="font-medium text-gray-900">
                {analysisResult.risk_level === 'high' ? 'High Risk' : 
                analysisResult.risk_level === 'medium' ? 'Medium Risk' : 
                'Low Risk'} - Score: {analysisResult.risk_score}/100
              </h3>
              <p className="text-sm text-gray-500">
                Invoice #{analysisResult.invoice_id}
              </p>
            </div>
          </div>
          
          <div className="space-y-3 mb-4">
            <h4 className="font-medium text-gray-700">Anomalies Detected</h4>
            {analysisResult.anomalies.length > 0 ? (
              analysisResult.anomalies.map((anomaly: any, index: number) => (
                <div key={index} className="p-3 bg-danger-50 rounded-lg">
                  <div className="flex items-start">
                    <Zap className="w-5 h-5 text-danger-600 mt-0.5 mr-3 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-gray-800">{anomaly.type}</p>
                      <p className="text-sm text-gray-600">{anomaly.message}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500">No anomalies detected</p>
            )}
          </div>
          
          <div className="space-y-3">
            <h4 className="font-medium text-gray-700">Recommendations</h4>
            {analysisResult.recommendations.map((rec: string, index: number) => (
              <div key={index} className="flex items-start">
                <CheckCircle className="w-5 h-5 text-success-600 mt-0.5 mr-3 flex-shrink-0" />
                <p className="text-sm text-gray-800">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search invoices..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <select 
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="flagged">Flagged</option>
                <option value="processing">Processing</option>
              </select>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">
              {filteredInvoices.length} invoices
            </span>
            {selectedInvoices.length > 0 && (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-primary-600">
                  {selectedInvoices.length} selected
                </span>
                <button className="px-3 py-1 bg-success-600 text-white text-xs font-medium rounded-full hover:bg-success-700">
                  Approve
                </button>
                <button className="px-3 py-1 bg-danger-600 text-white text-xs font-medium rounded-full hover:bg-danger-700">
                  Reject
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Invoice Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedInvoices.length === filteredInvoices.length && filteredInvoices.length > 0}
                    onChange={selectAllInvoices}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Invoice
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vendor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredInvoices.map((invoice, index) => (
                <tr 
                  key={invoice.id} 
                  className="hover:bg-gray-50 transition-colors duration-200 animate-slide-up"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type="checkbox"
                      checked={selectedInvoices.includes(invoice.id)}
                      onChange={() => toggleInvoiceSelection(invoice.id)}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{invoice.id}</div>
                      <div className="text-sm text-gray-500">{invoice.date}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="max-w-xs">
                      <div className="text-sm font-medium text-gray-900 truncate">{invoice.vendor}</div>
                      <div className="text-sm text-gray-500 truncate">{invoice.matter}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      ${invoice.amount.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-500">{invoice.category}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(invoice.status)}
                      <span className={getStatusBadge(invoice.status)}>
                        {invoice.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRiskColor(invoice.riskScore)}`}>
                      {invoice.riskScore}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button 
                      className="text-primary-600 hover:text-primary-900 mr-3"
                      onClick={() => analyzeInvoice(invoice.id)}
                      title="AI Analyze"
                    >
                      <Zap className="w-4 h-4" />
                    </button>
                    <button className="text-primary-600 hover:text-primary-900 mr-3" title="View Details">
                      <Eye className="w-4 h-4" />
                    </button>
                    <button className="text-success-600 hover:text-success-900 mr-3" title="Approve">
                      <CheckCircle className="w-4 h-4" />
                    </button>
                    <button className="text-danger-600 hover:text-danger-900" title="Reject">
                      <XCircle className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination would go here */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-500">
          Showing 1 to {filteredInvoices.length} of {filteredInvoices.length} results
        </div>
        <div className="flex items-center space-x-2">
          <button className="px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 hover:bg-gray-50">
            Previous
          </button>
          <button className="px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 hover:bg-gray-50">
            Next
          </button>
        </div>
      </div>
        </>
      )}
    </div>
  );
};

export default Invoices;