import React from 'react';
import { AlertTriangle, TrendingUp, Clock, DollarSign, FileX } from 'lucide-react';

const AlertsPanel: React.FC = () => {
  const alerts = [
    {
      id: 1,
      type: 'budget',
      severity: 'high',
      title: 'Budget Threshold Exceeded',
      message: 'IP Litigation matter has exceeded 90% of allocated budget',
      time: '2 hours ago',
      icon: DollarSign
    },
    {
      id: 2,
      type: 'anomaly',
      severity: 'medium',
      title: 'Unusual Billing Pattern',
      message: 'Baker McKenzie submitted 3x normal hours for Q4',
      time: '4 hours ago',
      icon: TrendingUp
    },
    {
      id: 3,
      type: 'approval',
      severity: 'low',
      title: 'Pending Approvals',
      message: '12 invoices requiring manager approval',
      time: '6 hours ago',
      icon: Clock
    },
    {
      id: 4,
      type: 'compliance',
      severity: 'high',
      title: 'Missing Documentation',
      message: 'Invoice #INV-2024-003 lacks required supporting docs',
      time: '1 day ago',
      icon: FileX
    }
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-danger-100 text-danger-700 border-danger-200';
      case 'medium':
        return 'bg-warning-100 text-warning-700 border-warning-200';
      case 'low':
        return 'bg-primary-100 text-primary-700 border-primary-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getIconColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'text-danger-500';
      case 'medium':
        return 'text-warning-500';
      case 'low':
        return 'text-primary-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">AI Insights & Alerts</h3>
          <p className="text-sm text-gray-500">System-generated notifications</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-danger-100 text-danger-700">
            4 active
          </span>
        </div>
      </div>
      
      <div className="space-y-4">
        {alerts.map((alert, index) => {
          const Icon = alert.icon;
          return (
            <div 
              key={alert.id}
              className={`p-4 rounded-lg border transition-all duration-200 hover:shadow-sm animate-slide-up ${getSeverityColor(alert.severity)}`}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <Icon className={`w-5 h-5 ${getIconColor(alert.severity)}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900">
                      {alert.title}
                    </p>
                    <span className="text-xs text-gray-500">{alert.time}</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">
                    {alert.message}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-6 pt-4 border-t border-gray-200">
        <button className="w-full text-sm text-primary-600 hover:text-primary-700 font-medium text-center">
          View All Alerts
        </button>
      </div>
    </div>
  );
};

export default AlertsPanel;