import React, { useState } from 'react';
import { FileText, AlertTriangle, CheckCircle, Clock, Loader2, ExternalLink } from 'lucide-react';
import { useInvoices } from '../hooks/useApi';
import { useNavigate } from 'react-router-dom';

const RecentInvoices: React.FC = () => {
  const navigate = useNavigate();
  const { invoices, loading, error } = useInvoices();
  const [selectedInvoice, setSelectedInvoice] = useState<string | null>(null);
  
  const handleViewInvoice = (id: string) => {
    setSelectedInvoice(id);
    navigate(`/invoices/${id}`);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-4 h-4 text-success-500" />;
      case 'flagged':
        return <AlertTriangle className="w-4 h-4 text-danger-500" />;
      case 'pending':
      case 'processing':
        return <Clock className="w-4 h-4 text-warning-500" />;
      default:
        return <FileText className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = "px-2 py-1 text-xs font-medium rounded-full";
    switch (status) {
      case 'approved':
        return `${baseClasses} bg-success-100 text-success-700`;
      case 'flagged':
        return `${baseClasses} bg-danger-100 text-danger-700`;
      case 'pending':
        return `${baseClasses} bg-warning-100 text-warning-700`;
      case 'processing':
        return `${baseClasses} bg-primary-100 text-primary-700`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-700`;
    }
  };

  const getRiskBadge = (riskScore: number) => {
    const baseClasses = "px-2 py-1 text-xs font-medium rounded-full";
    
    if (riskScore >= 70) {
      return `${baseClasses} bg-danger-100 text-danger-700`;
    } else if (riskScore >= 30) {
      return `${baseClasses} bg-warning-100 text-warning-700`;
    } else {
      return `${baseClasses} bg-success-100 text-success-700`;
    }
  };
  
  const getRiskLabel = (riskScore: number) => {
    if (riskScore >= 70) {
      return 'high';
    } else if (riskScore >= 30) {
      return 'medium';
    } else {
      return 'low';
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Recent Invoices</h3>
          <p className="text-sm text-gray-500">Latest invoice submissions and status</p>
        </div>
        <button 
          onClick={() => navigate('/invoices')}
          className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center"
        >
          View All <ExternalLink className="ml-1 w-3 h-3" />
        </button>
      </div>
      
      <div className="overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="w-6 h-6 text-primary-500 animate-spin" />
            <span className="ml-2 text-sm text-gray-500">Loading invoices...</span>
          </div>
        ) : error ? (
          <div className="p-4 text-center text-danger-600 bg-danger-50 rounded-lg">
            <p>Error loading invoices. Please try again.</p>
          </div>
        )        : (
          <div className="space-y-4">
            {invoices.slice(0, 5).map((invoice, index) => (
              <div 
                key={`invoice-${invoice.id}`}
                className="flex items-center justify-between p-4 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors duration-200 animate-slide-up cursor-pointer"
                style={{ animationDelay: `${index * 50}ms` }}
                onClick={() => handleViewInvoice(invoice.id)}
              >
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    {getStatusIcon(invoice.status)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {invoice.vendor}
                      </p>
                      <span className={getRiskBadge(invoice.riskScore)}>
                        {getRiskLabel(invoice.riskScore)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 truncate">{invoice.matter}</p>
                    <p className="text-xs text-gray-400">{invoice.id} • {invoice.date}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm font-semibold text-gray-900">
                      ${invoice.amount ? invoice.amount.toLocaleString() : '0'}
                    </p>
                    <span className={getStatusBadge(invoice.status)}>
                      {invoice.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentInvoices;