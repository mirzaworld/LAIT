import React from 'react';
import { Notification } from '../hooks/useNotifications';

interface NotificationItemProps {
    notification: Notification;
    onAction?: (action: string) => void;
}

export const NotificationItem: React.FC<NotificationItemProps> = ({
    notification,
    onAction
}) => {
    const getSeverityColor = (severity?: string) => {
        switch (severity) {
            case 'high':
            case 'error':
                return 'bg-red-100 dark:bg-red-800 text-red-800 dark:text-red-100';
            case 'medium':
            case 'warning':
                return 'bg-yellow-100 dark:bg-yellow-800 text-yellow-800 dark:text-yellow-100';
            case 'low':
            case 'info':
            default:
                return 'bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-100';
        }
    };
    
    const handleAction = (action: string) => {
        onAction?.(action);
    };
    
    const renderContent = () => {
        switch (notification.type) {
            case 'invoice_analysis':
                return (
                    <>
                        <div className="font-medium">
                            Invoice {notification.data.invoice_number}
                        </div>
                        <div className="text-sm">
                            Risk Score: {notification.data.risk_score}
                            {notification.data.risk_factors && notification.data.risk_factors.length > 0 && (
                                <ul className="mt-1">
                                    {notification.data.risk_factors.map((factor, index) => (
                                        <li key={index} className={`px-2 py-1 my-1 rounded ${getSeverityColor(factor.severity)}`}>
                                            {factor.description}
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                        {notification.data.recommendations && notification.data.recommendations.length > 0 && (
                            <div className="mt-2">
                                <strong>Recommendations:</strong>
                                <ul className="mt-1">
                                    {notification.data.recommendations.map((rec, index) => (
                                        <li key={index} className="text-sm">
                                            • {rec.description}
                                            {rec.potential_savings && (
                                                <span className="text-green-600 dark:text-green-400 ml-1">
                                                    (Potential savings: ${rec.potential_savings.toLocaleString()})
                                                </span>
                                            )}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        <div className="mt-2 flex gap-2">
                            <button
                                onClick={() => handleAction('view')}
                                className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                            >
                                View Details
                            </button>
                            <button
                                onClick={() => handleAction('approve')}
                                className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600"
                            >
                                Approve
                            </button>
                            <button
                                onClick={() => handleAction('reject')}
                                className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                            >
                                Reject
                            </button>
                        </div>
                    </>
                );
                
            case 'vendor_update':
                return (
                    <>
                        <div className="font-medium">
                            Vendor Update: {notification.data.name}
                        </div>
                        <div className="text-sm">
                            Performance Score: {notification.data.performance_score}
                            <div className="mt-1">
                                Risk Profile: {notification.data.risk_profile}
                            </div>
                        </div>
                        <button
                            onClick={() => handleAction('viewVendor')}
                            className="mt-2 px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            View Vendor Details
                        </button>
                    </>
                );
                
            case 'alert':
            default:
                return (
                    <div className={`${getSeverityColor(notification.data.severity)}`}>
                        <div className="font-medium">
                            {notification.data.alert_type}
                        </div>
                        <div className="text-sm">
                            {notification.data.message}
                        </div>
                    </div>
                );
        }
    };
    
    return (
        <div className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow mb-4">
            {renderContent()}
            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                {new Date(notification.timestamp).toLocaleString()}
            </div>
        </div>
    );
};
