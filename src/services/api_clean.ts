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
  isAuthenticated,
  uploadInvoice,
  healthCheck,
};
