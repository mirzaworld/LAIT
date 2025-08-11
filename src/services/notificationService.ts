import axios from 'axios';

export interface Notification {
  id: string;
  type: 'success' | 'warning' | 'info' | 'error';
  message: string;
  timestamp: Date;
  read: boolean;
  link?: string;
  metadata?: {
    invoiceId?: string;
    vendorId?: string;
    amount?: number;
    riskScore?: number;
    category?: string;
  };
}

class NotificationService {
  private ws: WebSocket | null = null;
  private baseUrl: string;
  private listeners: ((notification: Notification) => void)[] = [];

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL || '/api';
    this.connect();
  }

  private connect() {
    const wsUrl = this.baseUrl.replace('http', 'ws') + '/ws/notifications';
    this.ws = new WebSocket(wsUrl);

    this.ws.onmessage = (event) => {
      const notification = JSON.parse(event.data);
      this.notifyListeners(notification);
    };

    this.ws.onclose = () => {
      // Reconnect after 5 seconds
      setTimeout(() => this.connect(), 5000);
    };
  }

  private notifyListeners(notification: Notification) {
    this.listeners.forEach(listener => listener(notification));
  }

  async getNotifications(limit = 50): Promise<Notification[]> {
    try {
      const response = await axios.get(`${this.baseUrl}/api/notifications`, {
        params: { limit }
      });
      return response.data.map((n: any) => ({
        ...n,
        timestamp: new Date(n.timestamp)
      }));
    } catch (error) {
      console.error('Error fetching notifications:', error);
      return [];
    }
  }

  async markAsRead(notificationId: string): Promise<boolean> {
    try {
      await axios.post(`${this.baseUrl}/api/notifications/${notificationId}/read`);
      return true;
    } catch (error) {
      console.error('Error marking notification as read:', error);
      return false;
    }
  }

  async markAllAsRead(): Promise<boolean> {
    try {
      await axios.post(`${this.baseUrl}/api/notifications/read-all`);
      return true;
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      return false;
    }
  }

  async deleteNotification(notificationId: string): Promise<boolean> {
    try {
      await axios.delete(`${this.baseUrl}/api/notifications/${notificationId}`);
      return true;
    } catch (error) {
      console.error('Error deleting notification:', error);
      return false;
    }
  }

  async clearAllNotifications(): Promise<boolean> {
    try {
      await axios.delete(`${this.baseUrl}/api/notifications`);
      return true;
    } catch (error) {
      console.error('Error clearing notifications:', error);
      return false;
    }
  }

  onNotification(callback: (notification: Notification) => void) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback);
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

export const notificationService = new NotificationService();
