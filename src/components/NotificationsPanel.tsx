import React, { useEffect } from 'react';
import { useNotifications } from '../hooks/useNotifications';
import { NotificationItem } from './NotificationItem';

interface Props { open?: boolean; onOpen?: () => void; }

const NotificationsPanel: React.FC<Props> = ({ open = true, onOpen }) => {
  const { notifications, clearNotifications, unread, onPanelOpen, acknowledge } = useNotifications();

  useEffect(() => {
    if (open) {
      onPanelOpen();
      onOpen?.();
    }
  }, [open, onOpen, onPanelOpen]);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 max-h-96 overflow-y-auto relative">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold flex items-center gap-2">Real-Time Notifications {unread > 0 && (<span className="ml-1 inline-flex items-center justify-center text-xs bg-red-600 text-white px-2 py-0.5 rounded-full">{unread}</span>)}</h3>
        <div className="flex gap-2">
          <button onClick={clearNotifications} className="text-xs text-blue-600 hover:underline">Clear</button>
        </div>
      </div>
      {notifications.length === 0 && (
        <div className="text-sm text-gray-500">No notifications yet.</div>
      )}
      {notifications.map((n, idx) => (
        <div key={n.id ?? idx} className={!n.read ? 'border-l-4 border-blue-500 pl-2' : ''}>
          <NotificationItem notification={n as any} onAction={() => n.id && acknowledge(n.id)} />
        </div>
      ))}
    </div>
  );
};

export default NotificationsPanel;
