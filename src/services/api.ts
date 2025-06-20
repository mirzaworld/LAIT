// API service for interacting with the backend

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5003';

// Authentication helpers
const getAuthToken = (): string | null => {
  return localStorage.getItem('lait_token') || localStorage.getItem('token');
};

const getAuthHeaders = (): HeadersInit => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
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
    
    const response = await fetch(`${API_URL}/auth/login`, {
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
    let url = `${API_URL}/api/invoices`;
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
    const response = await fetch(`${API_URL}/api/invoices/${invoiceId}`, {
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
    const response = await fetch(`${API_URL}/api/invoices/${invoiceId}/analyze`, {
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
    
    console.log('Uploading invoice to:', `${API_URL}/api/upload-invoice`);
    
    // Don't include Content-Type header for FormData - let browser set it
    const headers = getAuthHeaders();
    delete (headers as any)['Content-Type'];
    
    const response = await fetch(`${API_URL}/api/upload-invoice`, {
      method: 'POST',
      body: formData,
      headers,
      mode: 'cors',
      credentials: 'omit'
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
    const response = await fetch(`${API_URL}/api/vendors`, {
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
    const response = await fetch(`${API_URL}/api/vendors/${vendorId}/performance`, {
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
    console.log('Fetching dashboard metrics from:', `${API_URL}/api/dashboard/metrics`);
    
    const response = await fetch(`${API_URL}/api/dashboard/metrics`, {
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
    let url = `${API_URL}/api/analytics/spend-trends`;
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
