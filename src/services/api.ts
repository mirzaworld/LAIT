// API service for interacting with the backend

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

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
  active_matters: number;
  vendor_count: number;
  avg_processing_time: number;
  risk_distribution: {
    high: number;
    medium: number;
    low: number;
  };
}

// API Functions

/**
 * Get all invoices with optional filters
 */
export const getInvoices = async (status?: string, vendor?: string): Promise<Invoice[]> => {
  try {
    let url = `${API_URL}/invoices`;
    const params = new URLSearchParams();
    
    if (status) params.append('status', status);
    if (vendor) params.append('vendor', vendor);
    
    if (params.toString()) {
      url += `?${params.toString()}`;
    }
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.invoices;
  } catch (error) {
    console.error('Error fetching invoices:', error);
    throw error;
  }
};

/**
 * Get detailed information for a specific invoice
 */
export const getInvoiceDetails = async (invoiceId: string): Promise<any> => {
  try {
    const response = await fetch(`${API_URL}/invoices/${invoiceId}`);
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
    const response = await fetch(`${API_URL}/invoices/${invoiceId}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
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
export const uploadInvoice = async (fileData: File): Promise<any> => {
  try {
    const formData = new FormData();
    formData.append('file', fileData);
    
    const response = await fetch(`${API_URL}/invoices/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error uploading invoice:', error);
    throw error;
  }
};

/**
 * Get all vendors
 */
export const getVendors = async (): Promise<Vendor[]> => {
  try {
    const response = await fetch(`${API_URL}/vendors`);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.vendors;
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
    const response = await fetch(`${API_URL}/vendors/${vendorId}/performance`);
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
    const response = await fetch(`${API_URL}/dashboard/metrics`);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching dashboard metrics:', error);
    throw error;
  }
};

/**
 * Get spend trends for analytics
 */
export const getSpendTrends = async (period: string = 'monthly', category?: string): Promise<any> => {
  try {
    let url = `${API_URL}/analytics/spend-trends`;
    const params = new URLSearchParams();
    
    params.append('period', period);
    if (category) params.append('category', category);
    
    url += `?${params.toString()}`;
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching spend trends:', error);
    throw error;
  }
};
