// LAIT Frontend API Client
// Real fetch implementation for backend at port 5003

/// <reference types="vite/client" />

export const API = import.meta.env.VITE_API_BASE || "/api";

// Helper function to handle fetch responses
const handleResponse = async (response: Response) => {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.error || errorData.message || errorMessage;
    } catch {
      // If JSON parsing fails, use status text
    }
    throw new Error(errorMessage);
  }
  return await response.json();
};

// Helper function to get auth token
const getToken = (): string | null => {
  return localStorage.getItem('lait_token') || localStorage.getItem('token');
};

// Helper function to create headers with auth
const createHeaders = (token?: string): HeadersInit => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  const authToken = token || getToken();
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  
  return headers;
};

// Authentication API
export const auth = {
  register: async (email: string, password: string, firstName?: string, lastName?: string, company?: string) => {
    const response = await fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        company,
      }),
    });
    
    const data = await handleResponse(response);
    
    // Store token if registration successful
    if (data.token) {
      localStorage.setItem('lait_token', data.token);
    }
    
    return data;
  },

  login: async (email: string, password: string) => {
    const response = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });
    
    const data = await handleResponse(response);
    
    // Store token if login successful
    if (data.token) {
      localStorage.setItem('lait_token', data.token);
    }
    
    return data;
  },

  me: async (token?: string) => {
    const response = await fetch(`${API}/auth/me`, {
      method: 'GET',
      headers: createHeaders(token),
    });
    
    return await handleResponse(response);
  },

  logout: () => {
    localStorage.removeItem('lait_token');
    localStorage.removeItem('token');
  },

  isAuthenticated: (): boolean => {
    return !!getToken();
  },
};

// Invoices API
export const invoices = {
  upload: async (file: File, token?: string, meta?: { vendor?: string; invoice_number?: string; date?: string }) => {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add metadata if provided
    if (meta?.vendor) {
      formData.append('vendor', meta.vendor);
    }
    if (meta?.invoice_number) {
      formData.append('invoice_number', meta.invoice_number);
    }
    if (meta?.date) {
      formData.append('date', meta.date);
    }
    
    const authToken = token || getToken();
    const headers: HeadersInit = {};
    
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const response = await fetch(`${API}/invoices/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });
    
    return await handleResponse(response);
  },

  uploadJSON: async (invoiceData: {
    vendor: string;
    invoice_number?: string;
    date?: string;
    lines: Array<{
      description: string;
      hours: number;
      rate: number;
    }>;
  }, token?: string) => {
    const response = await fetch(`${API}/invoices/upload`, {
      method: 'POST',
      headers: createHeaders(token),
      body: JSON.stringify(invoiceData),
    });
    
    return await handleResponse(response);
  },

  list: async (token?: string) => {
    const response = await fetch(`${API}/invoices`, {
      method: 'GET',
      headers: createHeaders(token),
    });
    
    return await handleResponse(response);
  },

  get: async (id: number, token?: string) => {
    const response = await fetch(`${API}/invoices/${id}`, {
      method: 'GET',
      headers: createHeaders(token),
    });
    
    return await handleResponse(response);
  },
};

// Analytics API
export const analytics = {
  summary: async (token?: string) => {
    const response = await fetch(`${API}/dashboard/metrics`, {
      method: 'GET',
      headers: createHeaders(token),
    });
    
    return await handleResponse(response);
  },

  spending: async (timeframe = '6months', token?: string) => {
    const response = await fetch(`${API}/analytics/spending?timeframe=${timeframe}`, {
      method: 'GET',
      headers: createHeaders(token),
    });
    
    return await handleResponse(response);
  },
};

// Health check
export const health = {
  check: async () => {
    const response = await fetch(`${API}/health`, {
      method: 'GET',
    });
    
    return await handleResponse(response);
  },
};

// Default export for convenience
export default {
  auth,
  invoices,
  analytics,
  health,
};
