import React from 'react';
import { FileText, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

const RecentInvoices: React.FC = () => {
  const invoices = [
    {
      id: 'INV-2024-001',
      vendor: 'Morrison & Foerster LLP',
      amount: 45750,
      status: 'approved',
      date: '2024-01-15',
      matter: 'IP Litigation - TechCorp',
      risk: 'low'
    },
    {
      id: 'INV-2024-002',
      vendor: 'Baker McKenzie',
      amount: 23400,
      status: 'pending',
      date: '2024-01-14',
      matter: 'M&A Advisory',
      risk: 'medium'
    },
    {
      id: 'INV-2024-003',
      vendor: 'Latham & Watkins',
      amount: 67800,
      status: 'flagged',
      date: '2024-01-13',
      matter: 'Regulatory Compliance',
      risk: 'high'
    },
    {
      id: 'INV-2024-004',
      vendor: 'Skadden Arps',
      amount: 34200,
      status: 'processing',
      date: '2024-01-12',
      matter: 'Employment Law',
      risk: 'low'
    },
    {
      id: 'INV-2024-005',
      vendor: 'White & Case',
      amount: 52300,
      status: 'approved',
      date: '2024-01-11',
      matter: 'International Trade',
      risk: 'medium'
    }
  ];

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

  const getRiskBadge = (risk: string) => {
    const baseClasses = "px-2 py-1 text-xs font-medium rounded-full";
    switch (risk) {
      case 'high':
        return `${baseClasses} bg-danger-100 text-danger-700`;
      case 'medium':
        return `${baseClasses} bg-warning-100 text-warning-700`;
      case 'low':
        return `${baseClasses} bg-success-100 text-success-700`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-700`;
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Recent Invoices</h3>
          <p className="text-sm text-gray-500">Latest invoice submissions and status</p>
        </div>
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          View All
        </button>
      </div>
      
      <div className="overflow-hidden">
        <div className="space-y-4">
          {invoices.map((invoice, index) => (
            <div 
              key={invoice.id}
              className="flex items-center justify-between p-4 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors duration-200 animate-slide-up"
              style={{ animationDelay: `${index * 50}ms` }}
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
                    <span className={getRiskBadge(invoice.risk)}>
                      {invoice.risk}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 truncate">{invoice.matter}</p>
                  <p className="text-xs text-gray-400">{invoice.id} • {invoice.date}</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-sm font-semibold text-gray-900">
                    ${invoice.amount.toLocaleString()}
                  </p>
                  <span className={getStatusBadge(invoice.status)}>
                    {invoice.status}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RecentInvoices;