// ===== TYPE DEFINITIONS =====

export interface Invoice {
  id: string;
  vendor: string;
  amount: number;
  date: string;
  status: string;
  description?: string;
  line_items?: any[];
  analysis?: any;
}

export interface Vendor {
  id: string;
  name: string;
  total_spent: number;
  invoice_count: number;
  average_amount: number;
  last_invoice_date: string;
}

export interface DashboardMetrics {
  total_invoices: number;
  total_amount: number;
  total_vendors: number;
  monthly_spending: number;
  top_vendors: Vendor[];
  recent_invoices: Invoice[];
  spending_by_month: any[];
}

export interface LiveInsight {
  id: string;
  type: string;
  title: string;
  description: string;
  value?: number;
  change?: number;
  timestamp: string;
}

export interface LiveDataStatus {
  status: 'active' | 'inactive' | 'error';
  last_update: string;
  sources_active: number;
  sources_total: number;
}

export interface MarketTrend {
  category: string;
  trend: 'up' | 'down' | 'stable';
  value: number;
  change_percent: number;
}

export interface RateBenchmark {
  category: string;
  market_rate: number;
  your_rate: number;
  variance_percent: number;
}

export interface LiveDataSource {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'error';
  last_update: string;
  type: string;
}

// API service for LAIT Real Backend
// Connects to backend with proper error handling and JWT auth

const VITE_API_BASE = import.meta.env.VITE_API_BASE || '';

// Helper function to construct API URLs
const apiUrl = (path: string): string => {
  // In development with Vite proxy, use relative paths
  if (import.meta.env.DEV || !VITE_API_BASE) {
    return path;
  }
  // In production, use full API base URL
  return `${VITE_API_BASE}${path}`;
};

// Get auth token from localStorage
const getAuthToken = (): string | null => {
  return localStorage.getItem('lait_token');
};

// Standard headers for API requests
const getHeaders = (includeAuth = true): HeadersInit => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  
  if (includeAuth) {
    const token = getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }
  
  return headers;
};

// Generic API request handler with error handling
const apiRequest = async (url: string, options: RequestInit = {}): Promise<any> => {
  try {
    const response = await fetch(apiUrl(url), {
      ...options,
      headers: {
        ...getHeaders(true),
        ...options.headers,
      },
    });

    // Handle non-200 responses by throwing an error
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || errorData.message || errorMessage;
      } catch {
        // If JSON parsing fails, use the status text
        errorMessage = response.statusText || `Request failed with status ${response.status}`;
      }
      
      throw new Error(errorMessage);
    }

    // Return parsed JSON response
    return await response.json();
  } catch (error) {
    console.error(`API request failed for ${url}:`, error);
    throw error;
  }
};

// ===== AUTHENTICATION API =====

export const auth = {
  /**
   * Register a new user
   */
  register: async (userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    company?: string;
  }): Promise<{ token: string; user: any; message: string }> => {
    const response = await apiRequest('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    
    // Store token if registration successful
    if (response.token) {
      localStorage.setItem('lait_token', response.token);
    }
    
    return response;
  },

  /**
   * Login user
   */
  login: async (email: string, password: string): Promise<{ token: string; user: any; message: string }> => {
    const response = await apiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    // Store token if login successful
    if (response.token) {
      localStorage.setItem('lait_token', response.token);
    }
    
    return response;
  },

  /**
   * Get current user info
   */
  me: async (): Promise<any> => {
    return await apiRequest('/api/auth/me');
  },

  /**
   * Logout user (clear token)
   */
  logout: (): void => {
    localStorage.removeItem('lait_token');
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: (): boolean => {
    return !!getAuthToken();
  }
};

// ===== INVOICES API =====

export const invoices = {
  /**
   * Upload and analyze an invoice file
   */
  upload: async (file: File): Promise<{
    message: string;
    invoice: any;
    analysis: any;
  }> => {
    const formData = new FormData();
    formData.append('file', file);

    const token = getAuthToken();
    const headers: HeadersInit = {};
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(apiUrl('/api/invoices/upload'), {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.message || errorMessage;
        } catch {
          errorMessage = response.statusText || `Upload failed with status ${response.status}`;
        }
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error('Invoice upload failed:', error);
      throw error;
    }
  },

  /**
   * Get list of invoices for current user
   */
  list: async (): Promise<{ invoices: any[] }> => {
    return await apiRequest('/api/invoices');
  },

  /**
   * Get specific invoice by ID
   */
  get: async (id: string): Promise<{ invoice: any }> => {
    return await apiRequest(`/api/invoices/${id}`);
  },
};

// ===== ANALYTICS API =====

export const analytics = {
  /**
   * Get analytics summary for dashboard
   */
  summary: async (): Promise<{
    total_invoices: number;
    total_amount: number;
    total_vendors: number;
    monthly_spending: number;
    top_vendors: any[];
    recent_invoices: any[];
    spending_by_month: any[];
  }> => {
    return await apiRequest('/api/analytics/summary');
  },

  /**
   * Get spending analytics over time
   */
  spending: async (timeframe = '6months'): Promise<{
    spending_by_month: any[];
    spending_by_vendor: any[];
    spending_categories: any[];
  }> => {
    return await apiRequest(`/api/analytics/spending?timeframe=${timeframe}`);
  },

  /**
   * Get vendor analysis
   */
  vendors: async (): Promise<{
    top_vendors: any[];
    vendor_trends: any[];
    new_vendors: any[];
  }> => {
    return await apiRequest('/api/analytics/vendors');
  },
};

// ===== NOTIFICATIONS API =====

export interface RawNotification {
  id?: number;
  type: string;
  timestamp: string;
  data: any;
  read?: boolean;
}

export const notifications = {
  /**
   * Get notifications for current user
   */
  list: async (): Promise<{ notifications: RawNotification[] }> => {
    return await apiRequest('/api/notifications');
  },

  /**
   * Get unread notification count
   */
  unreadCount: async (): Promise<{ count: number }> => {
    return await apiRequest('/api/notifications/unread-count');
  },

  /**
   * Acknowledge a notification (mark as read)
   */
  acknowledge: async (notificationId: number): Promise<{ message: string }> => {
    return await apiRequest(`/api/notifications/${notificationId}/ack`, {
      method: 'POST',
    });
  },

  /**
   * Mark all notifications as read
   */
  markAllRead: async (): Promise<{ message: string }> => {
    return await apiRequest('/api/notifications/mark-all-read', {
      method: 'POST',
    });
  },
};

// Notification helper functions for backward compatibility
export const getNotifications = async (): Promise<RawNotification[]> => {
  const response = await notifications.list();
  return response.notifications || [];
};

export const getUnreadNotificationCount = async (): Promise<number> => {
  try {
    const response = await notifications.unreadCount();
    return response.count || 0;
  } catch {
    return 0;
  }
};

export const ackNotification = async (notificationId: number): Promise<void> => {
  await notifications.acknowledge(notificationId);
};

export const markAllNotificationsRead = async (): Promise<void> => {
  await notifications.markAllRead();
};

// ===== LEGACY API FUNCTIONS =====
// These functions provide backward compatibility for existing hooks

export const getInvoices = async (): Promise<Invoice[]> => {
  try {
    const response = await invoices.list();
    return response.invoices || [];
  } catch (error) {
    console.error('Failed to fetch invoices:', error);
    return [];
  }
};

export const getVendors = async (): Promise<Vendor[]> => {
  try {
    const response = await analytics.vendors();
    return response.top_vendors || [];
  } catch (error) {
    console.error('Failed to fetch vendors:', error);
    return [];
  }
};

export const getDashboardMetrics = async (): Promise<DashboardMetrics> => {
  try {
    return await analytics.summary();
  } catch (error) {
    console.error('Failed to fetch dashboard metrics:', error);
    return {
      total_invoices: 0,
      total_amount: 0,
      total_vendors: 0,
      monthly_spending: 0,
      top_vendors: [],
      recent_invoices: [],
      spending_by_month: [],
    };
  }
};

export const getSpendTrends = async (timeframe = '6months'): Promise<any[]> => {
  try {
    const response = await analytics.spending(timeframe);
    return response.spending_by_month || [];
  } catch (error) {
    console.error('Failed to fetch spend trends:', error);
    return [];
  }
};

// ===== LIVE DATA API FUNCTIONS =====

export const getLiveInsights = async (): Promise<LiveInsight[]> => {
  // Mock data for live insights since backend doesn't have this endpoint yet
  return [
    {
      id: '1',
      type: 'cost_optimization',
      title: 'Potential Savings Identified',
      description: 'Found $12,000 in overspend across 3 vendors this month',
      value: 12000,
      change: 15.2,
      timestamp: new Date().toISOString(),
    },
    {
      id: '2', 
      type: 'rate_analysis',
      title: 'Rate Benchmark Alert',
      description: 'Partner rates 18% above market average for corporate law',
      value: 18,
      change: -2.1,
      timestamp: new Date().toISOString(),
    }
  ];
};

export const getLiveDataStatus = async (): Promise<LiveDataStatus> => {
  // Mock status data
  return {
    status: 'active',
    last_update: new Date().toISOString(),
    sources_active: 12,
    sources_total: 15,
  };
};

export const getMarketTrends = async (): Promise<MarketTrend[]> => {
  // Mock market trends data
  return [
    { category: 'Corporate Law', trend: 'up', value: 450, change_percent: 3.2 },
    { category: 'Litigation', trend: 'down', value: 380, change_percent: -1.8 },
    { category: 'IP Law', trend: 'stable', value: 520, change_percent: 0.5 },
  ];
};

export const getRateBenchmarks = async (): Promise<RateBenchmark[]> => {
  // Mock rate benchmarks data
  return [
    { category: 'Partner', market_rate: 450, your_rate: 475, variance_percent: 5.6 },
    { category: 'Senior Associate', market_rate: 320, your_rate: 310, variance_percent: -3.1 },
    { category: 'Associate', market_rate: 220, your_rate: 235, variance_percent: 6.8 },
  ];
};

// Additional missing functions for build compatibility
export const getLiveDataSources = async (): Promise<LiveDataSource[]> => {
  return [
    { id: '1', name: 'Legal Rate API', status: 'active', last_update: new Date().toISOString(), type: 'market_data' },
    { id: '2', name: 'Court Records', status: 'active', last_update: new Date().toISOString(), type: 'public_data' },
  ];
};

export const triggerLiveDataCollection = async (): Promise<{ message: string }> => {
  return { message: 'Live data collection triggered successfully' };
};

export const getCourtData = async (): Promise<any[]> => {
  return [];
};

export const getLegalMarketAnalysis = async (): Promise<any> => {
  return {};
};

export const uploadWithAI = async (file: File): Promise<any> => {
  // Fallback to regular upload
  return await invoices.upload(file);
};

export const analyzePDFWithAI = async (file: File): Promise<any> => {
  // Fallback to regular upload
  return await invoices.upload(file);
};

// Additional analytics and prediction functions
export const getAnalyticsData = async (): Promise<any> => {
  return await analytics.summary();
};

export const getVendorAnalytics = async (): Promise<any> => {
  return await analytics.vendors();
};

export const getPredictiveAnalytics = async (): Promise<any> => {
  return { predictions: [], trends: [], recommendations: [] };
};

// ===== UTILITY FUNCTIONS =====

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  return auth.isAuthenticated();
};

/**
 * Quick upload function for backward compatibility
 */
export const uploadInvoice = async (file: File): Promise<any> => {
  return await invoices.upload(file);
};

/**
 * API health check
 */
export const healthCheck = async (): Promise<{ status: string; message: string }> => {
  try {
    const response = await fetch(apiUrl('/api/health'), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    throw new Error('Backend service unavailable');
  }
};

// Default export for convenience
export default {
  auth,
  invoices,
  analytics,
  notifications,
  isAuthenticated,
  uploadInvoice,
  healthCheck,
};
