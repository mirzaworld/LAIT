import io, { Socket } from 'socket.io-client';
import { useEffect, useState, useCallback, useRef } from 'react';
import { toast } from 'react-toastify';
import { getNotifications as fetchNotifications, getUnreadNotificationCount, ackNotification, markAllNotificationsRead, RawNotification } from '../services/api';

export interface Notification {
    type: 'invoice_analysis' | 'alert' | 'vendor_update' | 'system_status' | 'self_test' | string;
    timestamp: string;
    data: any; // generalized for multiple backend formats
    id?: number;
    read?: boolean;
}

export const useNotifications = () => {
    const [socket, setSocket] = useState<Socket | null>(null);
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [unread, setUnread] = useState<number>(0);
    const panelOpenedRef = useRef(false);

    // Initialize socket + initial fetch
    useEffect(() => {
        const init = async () => {
            try {
                // Initial REST fetch
                try {
                    const [list, unreadCount] = await Promise.all([
                        fetchNotifications(50).catch(() => []),
                        getUnreadNotificationCount().catch(() => 0)
                    ]);
                    const normalized: Notification[] = list.map(n => ({
                        id: n.id,
                        type: n.type || n?.data?.type || 'alert',
                        timestamp: n.timestamp,
                        read: n.read,
                        data: n.data || { message: n.message, ...n.metadata }
                    }));
                    setNotifications(normalized);
                    setUnread(unreadCount);
                } catch (e) {
                    // Non-fatal
                    // eslint-disable-next-line no-console
                    console.warn('Notification bootstrap failed', e);
                }

                const SOCKET_ENABLED = import.meta.env.VITE_SOCKET_ENABLED === 'true' || true;
                if (SOCKET_ENABLED) {
                    const newSocket: Socket = io(import.meta.env.VITE_API_URL || 'http://localhost:5003');
                    setSocket(newSocket);
                    newSocket.on('connect_error', (err) => {
                        console.log('Socket connection error:', err.message);
                    });
                }
            } catch (err) {
                console.error('Failed to init notifications:', err);
            }
        };
        init();
        return () => { socket?.close(); };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Socket listeners
    useEffect(() => {
        if (!socket) return;
        const handleNotification = (raw: any) => {
            const n: Notification = {
                id: raw.id,
                type: raw.type,
                timestamp: raw.timestamp || new Date().toISOString(),
                read: false,
                data: raw.data || { message: raw.message, ...raw.metadata }
            };
            setNotifications(prev => [n, ...prev]);
            setUnread(u => u + 1);
            displayToast(n);
        };
        const handleUnreadCount = (payload: any) => {
            if (typeof payload?.unread === 'number') setUnread(payload.unread);
        };
        socket.on('notification', handleNotification);
        socket.on('notification_unread_count', handleUnreadCount);
        socket.on('system_status', (status: any) => {
            displayToast({ type: 'system_status', timestamp: new Date().toISOString(), data: status });
        });
        return () => {
            socket.off('notification', handleNotification);
            socket.off('notification_unread_count', handleUnreadCount);
            socket.off('system_status');
        };
    }, [socket]);

    const displayToast = (notification: Notification) => {
        switch (notification.type) {
            case 'invoice_analysis': {
                const risk = notification.data?.risk_score;
                const severity = risk > 70 ? 'error' : risk > 50 ? 'warning' : 'info';
                (toast as any)[severity]?.(`Invoice ${notification.data?.invoice_number} analyzed - Risk Score: ${risk}`);
                break;
            }
            case 'alert':
                (toast as any)[notification.data?.severity || 'info']?.(notification.data?.message || 'Alert');
                break;
            case 'vendor_update':
                toast.info(`Vendor ${notification.data?.name} performance updated: ${notification.data?.performance_score}`);
                break;
            case 'self_test':
                toast.success('System self-test completed');
                break;
            default:
                toast.info(notification.data?.message || notification.type);
        }
    };

    const acknowledge = useCallback(async (id: number) => {
        // Optimistic update
        setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
        setUnread(u => Math.max(0, u - 1));
        try {
            const res = await ackNotification(id);
            if (typeof res.unread === 'number') setUnread(res.unread);
        } catch (e) {
            console.warn('Ack failed, reverting', e);
        }
    }, []);

    const markAllRead = useCallback(async () => {
        // Mark visible unread
        const unreadIds = notifications.filter(n => !n.read && n.id != null).map(n => n.id as number);
        setNotifications(prev => prev.map(n => unreadIds.includes(n.id as number) ? { ...n, read: true } : n));
        const prevUnread = unread;
        setUnread(0);
        try {
            await markAllNotificationsRead();
        } catch (e) {
            console.warn('Mark-all-read failed, reverting');
            setUnread(prevUnread);
            setNotifications(prev => prev.map(n => unreadIds.includes(n.id as number) ? { ...n, read: false } : n));
        }
    }, [notifications, unread]);

    const onPanelOpen = useCallback(() => {
        if (!panelOpenedRef.current) {
            panelOpenedRef.current = true;
            // Delay a tick to avoid blocking UI
            setTimeout(() => { markAllRead(); }, 300);
        } else {
            // subsequent opens just sync unread count from server
            getUnreadNotificationCount().then(c => setUnread(c)).catch(()=>{});
        }
    }, [markAllRead]);

    return {
        notifications,
        unread,
        acknowledge,
        markAllRead,
        onPanelOpen,
        clearNotifications: () => setNotifications([])
    };
};
