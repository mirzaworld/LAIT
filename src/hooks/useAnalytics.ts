import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

export interface AnalyticsData {
  summary: {
    total: number;
    change: number;
    periodLabel: string;
  };
  trends: {
    labels: string[];
    values: number[];
  };
  breakdown: {
    labels: string[];
    values: number[];
  };
  details: {
    id: string;
    label: string;
    value: number;
    change: number;
    metadata?: any;
  }[];
}

export interface AnalyticsFilters {
  type?: string;
  startDate?: Date;
  endDate?: Date;
  timeframe?: string;
  category?: string;
}

export const useAnalytics = (filters: AnalyticsFilters) => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.get('/api/analytics', { params: filters });
        setData(response.data);
      } catch (err: any) {
        console.error('Error fetching analytics:', err);
        setError(err?.response?.data?.message || 'Failed to fetch analytics data');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [filters.type, filters.startDate, filters.endDate, filters.timeframe, filters.category]);

  const exportAnalytics = async () => {
    try {
      const response = await axios.post('/api/analytics/export', filters, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `analytics_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (err) {
      console.error('Error exporting analytics:', err);
      return false;
    }
  };

  return {
    data,
    loading,
    error,
    exportAnalytics
  };
};

export interface PerformanceMetrics {
  [key: string]: {
    current: number;
    previous: number;
    change: number;
    target?: number;
  };
}

export const usePerformanceMetrics = (type: string, timeframe: string) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.get('/api/performance-metrics', {
          params: { type, timeframe }
        });
        setMetrics(response.data);
      } catch (err: any) {
        console.error('Error fetching performance metrics:', err);
        setError(err?.response?.data?.message || 'Failed to fetch performance metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [type, timeframe]);

  return {
    metrics,
    loading,
    error
  };
};

export interface AIInsight {
  id: string;
  type: 'warning' | 'success' | 'info';
  message: string;
  priority: 'high' | 'medium' | 'low';
  metadata?: any;
}

export const useAIInsights = (filters: AnalyticsFilters) => {
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInsights = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.get('/api/ai-insights', {
          params: filters
        });
        setInsights(response.data);
      } catch (err: any) {
        console.error('Error fetching AI insights:', err);
        setError(err?.response?.data?.message || 'Failed to fetch AI insights');
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, [filters.type, filters.startDate, filters.endDate, filters.timeframe, filters.category]);

  return {
    insights,
    loading,
    error
  };
};

// Vendor Analysis Hook
export interface VendorAnalysis {
  vendorId: string;
  spendOverTime: Array<{
    date: string;
    amount: number;
    benchmark?: number;
  }>;
  categories: Array<{
    name: string;
    value: number;
  }>;
  performanceMetrics: Array<{
    name: string;
    value: number;
    benchmark?: number;
  }>;
  insights: string[];
  recommendations: string[];
}

export const useVendorAnalysis = (vendorId?: string, timeframe: '1m' | '3m' | '6m' | '1y' | 'all' = '6m') => {
  const [data, setData] = useState<VendorAnalysis | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      let url = `/api/analytics/vendors`;
      
      if (vendorId) {
        url += `/${vendorId}`;
      }
      
      url += `?timeframe=${timeframe}`;
      
      const response = await axios.get(url);
      setData(response.data);
    } catch (err: any) {
      setError(err?.response?.data?.message || 'Failed to fetch vendor analysis');
      console.error('Error fetching vendor analysis:', err);
    } finally {
      setLoading(false);
    }
  }, [vendorId, timeframe]);
  
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  return { data, loading, error, refetch: fetchData };
};

// Document Analysis Hook
export interface DocumentAnalysis {
  documentId: string;
  riskScore: number;
  anomalies: Array<{
    type: string;
    message: string;
    severity: 'low' | 'medium' | 'high';
  }>;
  entities: Array<{
    name: string;
    type: string;
    confidence: number;
  }>;
  summary: string;
  keywords: string[];
}

export const useDocumentAnalysis = (documentId: string) => {
  const [data, setData] = useState<DocumentAnalysis | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/documents/${documentId}/analyze`);
      setData(response.data);
    } catch (err: any) {
      setError(err?.response?.data?.message || 'Failed to fetch document analysis');
      console.error('Error fetching document analysis:', err);
    } finally {
      setLoading(false);
    }
  }, [documentId]);
  
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  return { data, loading, error, refetch: fetchData };
};

// Workflow Status Hook
export interface WorkflowStatus {
  workflowId: string;
  name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  progress: number;
  steps: Array<{
    name: string;
    status: 'pending' | 'in_progress' | 'completed' | 'error';
    startedAt?: string;
    completedAt?: string;
    message?: string;
  }>;
  createdAt: string;
  updatedAt: string;
}

export const useWorkflowStatus = (workflowId: string) => {
  const [data, setData] = useState<WorkflowStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/workflows/${workflowId}`);
      setData(response.data);
    } catch (err: any) {
      setError(err?.response?.data?.message || 'Failed to fetch workflow status');
      console.error('Error fetching workflow status:', err);
    } finally {
      setLoading(false);
    }
  }, [workflowId]);
  
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  return { data, loading, error, refetch: fetchData };
};

export default useAnalytics;
