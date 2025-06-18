import React, { useState } from 'react';
import { AlertTriangle, TrendingUp, Clock, DollarSign, FileX, ExternalLink, Loader2, Check } from 'lucide-react';
import { mockAlerts } from '../data/mockData';

const AlertsPanel: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [alerts, setAlerts] = useState(mockAlerts);
  const [resolvedAlerts, setResolvedAlerts] = useState<number[]>([]);
  
  const handleResolveAlert = (id: number, event: React.MouseEvent) => {
    event.stopPropagation();
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setResolvedAlerts([...resolvedAlerts, id]);
      setLoading(false);
    }, 500);
  };
  
  const handleViewAlert = (id: number) => {
    // In a real app, this would navigate to a detailed view or open a modal
    alert(`Viewing alert details for ID: ${id}`);
  };
  
  const getIcon = (iconType: string) => {
    switch (iconType) {
      case 'dollar':
        return DollarSign;
      case 'trend':
        return TrendingUp;
      case 'clock':
        return Clock;
      case 'file':
        return FileX;
      default:
        return AlertTriangle;
    }
  };

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
            {alerts.length - resolvedAlerts.length} active
          </span>
        </div>
      </div>
      
      {loading ? (
        <div className="flex items-center justify-center p-8">
          <Loader2 className="w-6 h-6 text-primary-500 animate-spin" />
          <span className="ml-2 text-sm text-gray-500">Processing...</span>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert, index) => {
            const isResolved = resolvedAlerts.includes(alert.id);
            const IconComponent = getIcon(alert.icon);
            
            return (
              <div 
                key={alert.id}
                onClick={() => !isResolved && handleViewAlert(alert.id)}
                className={`p-4 rounded-lg border transition-all duration-200 hover:shadow-sm animate-slide-up ${
                  isResolved ? 'bg-gray-50 border-gray-200 opacity-60' : getSeverityColor(alert.severity)
                } ${!isResolved ? 'cursor-pointer' : ''}`}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    {isResolved ? (
                      <Check className="w-5 h-5 text-success-500" />
                    ) : (
                      <IconComponent className={`w-5 h-5 ${getIconColor(alert.severity)}`} />
                    )}
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
                    {!isResolved && (
                      <div className="mt-2 flex justify-end">
                        <button 
                          onClick={(e) => handleResolveAlert(alert.id, e)}
                          className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                        >
                          Mark as resolved
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      <div className="mt-6 pt-4 border-t border-gray-200">
        <button 
          onClick={() => alert('Navigating to Alerts Dashboard')}
          className="w-full text-sm text-primary-600 hover:text-primary-700 font-medium text-center flex items-center justify-center"
        >
          View All Alerts <ExternalLink className="ml-1 w-3 h-3" />
        </button>
      </div>
    </div>
  );
};

export default AlertsPanel;