// API service for interacting with the backend

const API_URL = import.meta.env.VITE_API_URL || '';

// Helper function to construct API URLs
const apiUrl = (path: string) => {
  // In development, always use the Vite proxy (relative paths)
  // In production, use the full API_URL if provided
  if (import.meta.env.DEV || !API_URL) {
    // Use Vite's proxy in development
    return path;
  }
  
  // Production: use full API URL
  if (API_URL) {
    // Remove /api from API_URL if it exists to avoid duplication
    const baseUrl = API_URL.replace(/\/api$/, '');
    return `${baseUrl}${path}`;
  }
  
  // Fallback to relative paths
  return path;
};

// Authentication helpers
const getAuthToken = (): string | null => {
  return localStorage.getItem('lait_token') || localStorage.getItem('token');
};

// Refresh token if needed
const refreshTokenIfNeeded = async () => {
  const token = getAuthToken();
  if (!token) return;
  
  try {
    const response = await fetch(apiUrl('/auth/refresh'), {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    
    if (response.ok) {
      const { token: newToken } = await response.json();
      localStorage.setItem('lait_token', newToken);
    }
  } catch (error) {
    console.error('Token refresh failed:', error);
  }
};

const getAuthHeaders = (): HeadersInit => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Origin': window.location.origin,
    // In development, use mock token if no real token is available
    'Authorization': token ? `Bearer ${token}` : 'Bearer mock-jwt-token-for-development'
  };
};

// Authentication functions
export const login = async (email: string, password: string): Promise<{ token: string; user: any }> => {
  try {
    // For development, create a mock token
    if (email === 'admin@lait.demo' && password === 'demo123') {
      const mockToken = 'mock-jwt-token-for-development';
      localStorage.setItem('lait_token', mockToken);
      return {
        token: mockToken,
        user: {
          id: '1',
          email: 'admin@lait.demo',
          name: 'Admin User',
          role: 'admin'
        }
      };
    }
    
    const response = await fetch(apiUrl('/api/auth/login'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });
    
    if (!response.ok) {
      throw new Error('Invalid credentials');
    }
    
    const data = await response.json();
    localStorage.setItem('lait_token', data.token);
    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

export const logout = (): void => {
  localStorage.removeItem('lait_token');
  localStorage.removeItem('token');
};

export const isAuthenticated = (): boolean => {
  const token = getAuthToken();
  return !!token;
};

// Types
export interface Invoice {
  id: string;
  vendor: string;
  amount: number;
  status: string;
  date: string;
  dueDate: string;
  matter: string;
  riskScore: number;
  category: string;
  description: string;
  hours: number;
  rate: number;
  total: number;
}

export interface InvoiceAnalysis {
  invoice_id: string;
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high';
  anomalies: Array<{
    type: string;
    message: string;
    severity?: string;
  }>;
  recommendations: string[];
}

export interface Vendor {
  id: string;
  name: string;
  category: string;
  spend: number;
  matter_count: number;
  avg_rate: number;
  performance_score: number;
  diversity_score: number;
  on_time_rate: number;
}

export interface VendorPerformance {
  vendor: Vendor;
  metrics: {
    billing_efficiency: number;
    budget_adherence: number;
    timekeeper_distribution: {
      partner: number;
      senior_associate: number;
      junior_associate: number;
      paralegal: number;
    };
    average_invoice_processing: number;
    historical_rates: Array<{
      year: number;
      avg_rate: number;
    }>;
  };
  comparison: {
    rate_percentile: number;
    efficiency_percentile: number;
    diversity_percentile: number;
  };
  recommendations: Array<{
    category: string;
    text: string;
  }>;
}

export interface DashboardMetrics {
  total_spend: number;
  spend_change_percentage: number;
  invoice_count: number;
  active_matters: number;
  risk_factors_count: number;
  high_risk_invoices_count: number;
  avg_processing_time: number;
  date_range: {
    from: string;
    to: string;
  };
  trend_data: {
    monthly_spend: Array<{
      period: string;
      amount: number;
    }>;
  };
}

// API Functions

/**
 * Get all invoices with optional filters
 */
export const getInvoices = async (status?: string, vendor?: string): Promise<Invoice[]> => {
  try {
    let url = apiUrl('/api/invoices');
    const params = new URLSearchParams();
    
    if (status) params.append('status', status);
    if (vendor) params.append('vendor', vendor);
    
    if (params.toString()) {
      url += `?${params.toString()}`;
    }
    
    console.log('Fetching invoices from:', url);
    
    const response = await fetch(url, {
      headers: getAuthHeaders(),
      mode: 'cors',
      credentials: 'omit'
    });
    
    console.log('Invoice response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('API error response:', errorText);
      throw new Error(`API error (${response.status}): ${response.statusText} - ${errorText}`);
    }
    
    const data = await response.json();
    console.log('Invoice data received:', data.length, 'invoices');
    return data; // Backend returns invoices array directly
  } catch (error) {
    console.error('Error fetching invoices:', error);
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Unable to connect to the API server. Please ensure the backend is running on ${API_URL}`);
    }
    throw error;
  }
};

/**
 * Get detailed information for a specific invoice
 */
export const getInvoiceDetails = async (invoiceId: string): Promise<any> => {
  try {
    const response = await fetch(apiUrl(`/api/invoices/${invoiceId}`), {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching invoice details for ${invoiceId}:`, error);
    throw error;
  }
};

/**
 * Analyze an invoice using AI
 */
export const analyzeInvoice = async (invoiceId: string): Promise<InvoiceAnalysis> => {
  try {
    const response = await fetch(apiUrl(`/api/invoices/${invoiceId}/analyze`), {
      method: 'POST',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error analyzing invoice ${invoiceId}:`, error);
    throw error;
  }
};

/**
 * Upload a new invoice
 */
export const uploadInvoice = async (
  fileData: File, 
  vendor?: string,
  amount?: number,
  date?: string,
  category?: string,
  description?: string
): Promise<any> => {
  try {
    const formData = new FormData();
    formData.append('file', fileData);
    
    // Add additional metadata if provided
    if (vendor) formData.append('vendor', vendor);
    if (amount) formData.append('amount', amount.toString());
    if (date) formData.append('date', date);
    if (category) formData.append('category', category);
    if (description) formData.append('description', description);
    
    console.log('Uploading invoice to:', apiUrl('/api/upload-invoice'));
    
    // Don't include Content-Type header for FormData - let browser set it
    const headers = getAuthHeaders();
    delete (headers as any)['Content-Type'];
    
    const response = await fetch(apiUrl('/api/upload-invoice'), {
      method: 'POST',
      body: formData,
      headers: {
        ...headers,
        'Access-Control-Allow-Origin': window.location.origin,
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
      },
      mode: 'cors',
      credentials: 'include'
    });
    
    console.log('Upload response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Upload API error response:', errorText);
      throw new Error(`Upload API error (${response.status}): ${response.statusText} - ${errorText}`);
    }
    
    const data = await response.json();
    console.log('Upload successful:', data);
    return data;
  } catch (error) {
    console.error('Error uploading invoice:', error);
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Unable to connect to the API server. Please ensure the backend is running on ${API_URL}`);
    }
    throw error;
  }
};

/**
 * Get all vendors
 */
export const getVendors = async (): Promise<Vendor[]> => {
  try {
    const response = await fetch(apiUrl('/api/vendors'), {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data; // Backend returns vendors array directly
  } catch (error) {
    console.error('Error fetching vendors:', error);
    throw error;
  }
};

/**
 * Get performance metrics for a specific vendor
 */
export const getVendorPerformance = async (vendorId: string): Promise<VendorPerformance> => {
  try {
    const response = await fetch(apiUrl(`/api/vendors/${vendorId}/performance`), {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching performance for vendor ${vendorId}:`, error);
    throw error;
  }
};

/**
 * Get dashboard metrics
 */
export const getDashboardMetrics = async (): Promise<DashboardMetrics> => {
  try {
    console.log('Fetching dashboard metrics from:', `/api/dashboard/metrics`);
    
    const response = await fetch(apiUrl('/api/dashboard/metrics'), {
      headers: getAuthHeaders(),
      mode: 'cors',
      credentials: 'omit'
    });
    
    console.log('Metrics response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Metrics API error response:', errorText);
      throw new Error(`Metrics API error (${response.status}): ${response.statusText} - ${errorText}`);
    }
    
    const data = await response.json();
    console.log('Metrics data received:', data);
    return data;
  } catch (error) {
    console.error('Error fetching dashboard metrics:', error);
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Unable to connect to the API server. Please ensure the backend is running on ${API_URL}`);
    }
    throw error;
  }
};

/**
 * Get spend trends for analytics
 */
export const getSpendTrends = async (period: string = 'monthly', category?: string): Promise<any> => {
  try {
    let url = apiUrl('/api/analytics/spend-trends');
    const params = new URLSearchParams();
    
    params.append('period', period);
    if (category) params.append('category', category);
    
    url += `?${params.toString()}`;
    
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching spend trends:', error);
    throw error;
  }
};

/**
 * AI-powered PDF analysis
 */
export const analyzePDFWithAI = async (file: File): Promise<any> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = getAuthToken();
    const headers: HeadersInit = {
      'Accept': 'application/json'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(apiUrl('/api/ai/analyze-pdf'), {
      method: 'POST',
      headers,
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`AI PDF analysis failed: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error analyzing PDF with AI:', error);
    throw error;
  }
};

/**
 * Analyze contract text with AI
 */
export const analyzeContractWithAI = async (contractText: string): Promise<any> => {
  try {
    const response = await fetch(apiUrl('/api/ai/analyze-contract'), {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ text: contractText })
    });
    
    if (!response.ok) {
      throw new Error(`Contract analysis failed: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error analyzing contract with AI:', error);
    throw error;
  }
};

/**
 * Get legal insights from AI
 */
export const getLegalInsightsAI = async (query: string): Promise<any> => {
  try {
    const response = await fetch(apiUrl('/api/ai/legal-insights'), {
      method: 'POST', 
      headers: getAuthHeaders(),
      body: JSON.stringify({ query })
    });
    
    if (!response.ok) {
      throw new Error(`Legal insights failed: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error getting legal insights:', error);
    throw error;
  }
};

/**
 * Enhanced AI-powered file upload
 */
export const uploadWithAI = async (file: File, additionalData: any = {}): Promise<any> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add additional data to form
    Object.keys(additionalData).forEach(key => {
      if (additionalData[key] !== undefined && additionalData[key] !== null) {
        formData.append(key, additionalData[key].toString());
      }
    });
    
    const token = getAuthToken();
    const headers: HeadersInit = {
      'Accept': 'application/json'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(apiUrl('/api/ai/enhanced-upload'), {
      method: 'POST',
      headers,
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`AI upload failed: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error uploading with AI:', error);
    throw error;
  }
};

/**
 * Get GitHub legal tools
 */
export const getGitHubLegalTools = async (): Promise<any> => {
  try {
    const response = await fetch(apiUrl('/api/ai/github-tools'), {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`GitHub tools fetch failed: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching GitHub legal tools:', error);
    throw error;
  }
};

/**
 * LIVE DATA API FUNCTIONS - Real-time legal industry data
 */

// Live Data Types
export interface LiveDataSource {
  name: string;
  enabled: boolean;
  data_type: string;
  update_frequency: string;
  status: 'active' | 'inactive' | 'error';
  last_update?: string;
}

export interface LiveInsight {
  source: string;
  title: string;
  content: string;
  category: string;
  impact_score: number;
  relevance_score: number;
  created_at: string;
}

export interface MarketTrend {
  trend_type: string;
  description: string;
  trend_score: number;
  source: string;
  created_at: string;
}

export interface RateBenchmark {
  practice_area: string;
  seniority_level: string;
  avg_rate: number;
  market: string;
  source: string;
  created_at: string;
}

export interface LiveDataStatus {
  service_status: string;
  total_sources: number;
  active_sources: number;
  connected_sources: number;
  total_insights: number;
  recent_insights_24h: number;
  last_update: string;
}

/**
 * Get live data sources status
 */
export const getLiveDataSources = async (): Promise<{sources: LiveDataSource[], total_sources: number}> => {
  try {
    const response = await fetch(apiUrl('/api/live-data/sources'), {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Live data sources fetch failed: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching live data sources:', error);
    throw error;
  }
};

/**
 * Get live market insights
 */
export const getLiveInsights = async (limit: number = 20): Promise<LiveInsight[]> => {
  try {
    const response = await fetch(apiUrl(`/api/live-data/insights?limit=${limit}`), {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Live insights fetch failed: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.insights || data; // Handle different response formats
  } catch (error) {
    console.error('Error fetching live insights:', error);
    throw error;
  }
};

/**
 * Get rate benchmarks
 */
export const getRateBenchmarks = async (): Promise<RateBenchmark[]> => {
  try {
    const response = await fetch(apiUrl('/api/live-data/rate-benchmarks'), {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Rate benchmarks fetch failed: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.benchmarks || [];
  } catch (error) {
    console.error('Error fetching rate benchmarks:', error);
    throw error;  
  }
};

/**
 * Get market trends
 */
export const getMarketTrends = async (): Promise<MarketTrend[]> => {
  try {
    const response = await fetch(apiUrl('/api/live-data/market-trends'), {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Market trends fetch failed: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.trends || [];
  } catch (error) {
    console.error('Error fetching market trends:', error);
    throw error;
  }
};

/**
 * Get live data service status
 */
export const getLiveDataStatus = async (): Promise<LiveDataStatus> => {
  try {
    const response = await fetch(apiUrl('/api/live-data/status'), {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Live data status fetch failed: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching live data status:', error);
    throw error;
  }
};

/**
 * Trigger live data collection
 */
export const triggerLiveDataCollection = async (): Promise<any> => {
  try {
    const response = await fetch(apiUrl('/api/live-data/collect'), {
      method: 'POST',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Live data collection trigger failed: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error triggering live data collection:', error);
    throw error;
  }
};

/**
 * Get comprehensive analytics data
 */
export const getAnalyticsData = async (timeframe: string = '12M'): Promise<any> => {
  try {
    const response = await fetch(apiUrl(`/api/analytics/comprehensive?timeframe=${timeframe}`), {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Analytics data fetch failed: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching analytics data:', error);
    throw error;
  }
};

/**
 * Get vendor performance analytics
 */
export const getVendorAnalytics = async (): Promise<any> => {
  try {
    const response = await fetch(apiUrl('/api/analytics/vendor-performance'), {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Vendor analytics fetch failed: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching vendor analytics:', error);
    throw error;
  }
};

/**
 * Get predictive analytics
 */
export const getPredictiveAnalytics = async (): Promise<any> => {
  try {
    const response = await fetch(apiUrl('/api/analytics/predictive'), {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Predictive analytics fetch failed: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching predictive analytics:', error);
    throw error;
  }
};

/**
 * Get real-time court data
 */
export const getCourtData = async (): Promise<any> => {
  try {
    const response = await fetch(apiUrl('/api/legal-intelligence/court-data'), {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Court data fetch failed: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching court data:', error);
    throw error;
  }
};

/**
 * Get legal market analysis
 */
export const getLegalMarketAnalysis = async (): Promise<any> => {
  try {
    const response = await fetch(apiUrl('/api/legal-intelligence/market-analysis'), {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`Legal market analysis fetch failed: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching legal market analysis:', error);
    throw error;
  }
};

/**
 * Self-test API helper
 */
export const runSelfTest = async (): Promise<any> => {
  const response = await fetch(apiUrl('/api/self-test'), { headers: getAuthHeaders() });
  if (!response.ok) throw new Error('Self test failed');
  return response.json();
};

// ================= Notifications =================
export interface RawNotification {
  id?: number;
  type: string;
  message?: string; // DB stored notification_manager style
  metadata?: any;
  timestamp: string;
  read?: boolean;
  readAt?: string | null;
  data?: any; // legacy in-memory style (invoice_analysis, alert, etc.)
}

export const getNotifications = async (limit: number = 50): Promise<RawNotification[]> => {
  const response = await fetch(apiUrl(`/api/notifications?limit=${limit}`), { headers: getAuthHeaders() });
  if (!response.ok) throw new Error('Failed to fetch notifications');
  return await response.json();
};

export const getUnreadNotificationCount = async (): Promise<number> => {
  const response = await fetch(apiUrl('/api/notifications/unread-count'), { headers: getAuthHeaders() });
  if (!response.ok) throw new Error('Failed to fetch unread count');
  const data = await response.json();
  return data.unread || 0;
};

export const ackNotification = async (id: number): Promise<{ unread: number } > => {
  const response = await fetch(apiUrl(`/api/notifications/${id}/ack`), { method: 'POST', headers: getAuthHeaders() });
  if (!response.ok) throw new Error('Failed to acknowledge notification');
  return await response.json();
};

export const markAllNotificationsRead = async (): Promise<void> => {
  const response = await fetch(apiUrl('/api/notifications/read-all'), { method: 'POST', headers: getAuthHeaders() });
  if (!response.ok) throw new Error('Failed to mark all notifications read');
};
