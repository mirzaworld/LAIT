import { useState, useEffect } from 'react';
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

export default useAnalytics;
