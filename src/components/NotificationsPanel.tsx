import React from 'react';
import { useNotifications } from '../hooks/useNotifications';
import { NotificationItem } from './NotificationItem';

const NotificationsPanel: React.FC = () => {
  const { notifications, clearNotifications } = useNotifications();
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 max-h-96 overflow-y-auto">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold">Real-Time Notifications</h3>
        <button onClick={clearNotifications} className="text-xs text-blue-600 hover:underline">Clear</button>
      </div>
      {notifications.length === 0 && (
        <div className="text-sm text-gray-500">No notifications yet.</div>
      )}
      {notifications.map((n, idx) => (
        <NotificationItem key={idx} notification={n} />
      ))}
    </div>
  );
};

export default NotificationsPanel;
