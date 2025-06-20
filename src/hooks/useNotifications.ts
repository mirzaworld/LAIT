import { io, Socket } from 'socket.io-client';
import { useEffect, useState, useCallback } from 'react';
import { toast } from 'react-toastify';

export interface Notification {
    type: 'invoice_analysis' | 'alert' | 'vendor_update' | 'system_status';
    timestamp: string;
    data: {
        invoice_id?: number;
        invoice_number?: string;
        risk_score?: number;
        status?: string;
        amount?: number;
        risk_factors?: Array<{
            type: string;
            severity: string;
            description: string;
        }>;
        recommendations?: Array<{
            type: string;
            priority: string;
            description: string;
            rationale?: string;
            potential_savings?: number;
        }>;
        alert_type?: string;
        message?: string;
        severity?: string;
        vendor_id?: number;
        name?: string;
        performance_score?: number;
        risk_profile?: number;
        historical_performance?: any;
    };
}

export const useNotifications = () => {
    const [socket, setSocket] = useState<Socket | null>(null);
    const [notifications, setNotifications] = useState<Notification[]>([]);
    
    // Initialize socket connection
    useEffect(() => {
        const newSocket = io(import.meta.env.VITE_API_URL || 'http://localhost:8000');
        setSocket(newSocket);
        
        return () => {
            newSocket.close();
        };
    }, []);
    
    // Handle incoming notifications
    useEffect(() => {
        if (!socket) return;
        
        socket.on('notification', (notification: Notification) => {
            handleNotification(notification);
        });
        
        socket.on('system_status', (status: any) => {
            handleSystemStatus(status);
        });
        
        return () => {
            socket.off('notification');
            socket.off('system_status');
        };
    }, [socket]);
    
    const handleNotification = useCallback((notification: Notification) => {
        // Add notification to state
        setNotifications(prev => [notification, ...prev]);
        
        // Show appropriate toast notification based on type
        switch (notification.type) {
            case 'invoice_analysis':
                const { risk_score, invoice_number } = notification.data;
                const severity = risk_score && risk_score > 70 ? 'error' : 
                               risk_score && risk_score > 50 ? 'warning' : 'info';
                               
                toast[severity](`Invoice ${invoice_number} analyzed - Risk Score: ${risk_score}`, {
                    position: 'top-right',
                    autoClose: 5000
                });
                break;
                
            case 'alert':
                const { alert_type, message } = notification.data;
                toast[notification.data.severity || 'info'](message, {
                    position: 'top-right',
                    autoClose: 5000
                });
                break;
                
            case 'vendor_update':
                const { name, performance_score } = notification.data;
                toast.info(`Vendor ${name} performance updated: ${performance_score}`, {
                    position: 'top-right',
                    autoClose: 5000
                });
                break;
        }
    }, []);
    
    const handleSystemStatus = useCallback((status: any) => {
        console.log('System status update:', status);
        // Handle system status updates (e.g., model retraining, system maintenance)
    }, []);
    
    return {
        notifications,
        clearNotifications: () => setNotifications([])
    };
};
