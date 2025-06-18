import React, { createContext, useContext, useState, useCallback } from 'react';
import { useNotifications } from '../hooks/useNotifications';
import type { Notification } from '../hooks/useNotifications';

interface NotificationContextType {
    notifications: Notification[];
    hasUnread: boolean;
    markAllRead: () => void;
    clearNotifications: () => void;
}

const NotificationContext = createContext<NotificationContextType>({
    notifications: [],
    hasUnread: false,
    markAllRead: () => {},
    clearNotifications: () => {}
});

export const useNotificationContext = () => useContext(NotificationContext);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [readIds, setReadIds] = useState<Set<string>>(new Set());
    const { notifications, clearNotifications: clearAllNotifications } = useNotifications();
    
    const hasUnread = notifications.some(
        notification => !readIds.has(`${notification.type}-${notification.timestamp}`)
    );
    
    const markAllRead = useCallback(() => {
        const ids = notifications.map(
            notification => `${notification.type}-${notification.timestamp}`
        );
        setReadIds(new Set(ids));
    }, [notifications]);
    
    const clearNotifications = useCallback(() => {
        clearAllNotifications();
        setReadIds(new Set());
    }, [clearAllNotifications]);
    
    return (
        <NotificationContext.Provider
            value={{
                notifications,
                hasUnread,
                markAllRead,
                clearNotifications
            }}
        >
            {children}
        </NotificationContext.Provider>
    );
};
