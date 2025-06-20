import { useState, useEffect, useCallback } from 'react';
import { 
  getInvoices, 
  getVendors, 
  getDashboardMetrics, 
  getSpendTrends,
  Invoice,
  Vendor,
  DashboardMetrics
} from '../services/api';
import { mockInvoices, mockVendors, mockDashboardMetrics, mockSpendTrends } from '../data/mockData';

// Use this to toggle between API and mock data
const USE_MOCK_DATA = false; // Using real API data now that endpoints are working

export function useInvoices(status?: string, vendor?: string) {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInvoices = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      let data: Invoice[];
      
      if (USE_MOCK_DATA) {
        // Filter mock data based on status and vendor
        data = [...mockInvoices];
        
        if (status) {
          data = data.filter(invoice => invoice.status === status);
        }
        
        if (vendor) {
          data = data.filter(invoice => invoice.vendor === vendor);
        }
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));
      } else {
        data = await getInvoices(status, vendor);
      }
      
      setInvoices(data);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch invoices');
    } finally {
      setLoading(false);
    }
  }, [status, vendor]);

  useEffect(() => {
    fetchInvoices();
  }, [fetchInvoices]);

  return { invoices, loading, error, refetch: fetchInvoices };
}

export function useVendors() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchVendors = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      let data: Vendor[];
      
      if (USE_MOCK_DATA) {
        data = [...mockVendors];
        await new Promise(resolve => setTimeout(resolve, 500));
      } else {
        data = await getVendors();
      }
      
      setVendors(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch vendors');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchVendors();
  }, [fetchVendors]);

  return { vendors, loading, error, refetch: fetchVendors };
}

export function useDashboardMetrics() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      let data: DashboardMetrics;
      
      if (USE_MOCK_DATA) {
        data = {...mockDashboardMetrics};
        await new Promise(resolve => setTimeout(resolve, 500));
      } else {
        data = await getDashboardMetrics();
      }
      
      setMetrics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard metrics');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  return { metrics, loading, error, refetch: fetchMetrics };
}

export function useSpendTrends(period: string = 'monthly', category?: string) {
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTrends = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      let data;
      
      if (USE_MOCK_DATA) {
        data = {...mockSpendTrends};
        
        // Filter by period if needed
        if (period !== 'monthly') {
          // Simplify data based on period
          if (period === 'quarterly') {
            data = {
              ...data,
              labels: ['Q1', 'Q2', 'Q3', 'Q4'],
              datasets: data.datasets.map((dataset: any) => ({
                ...dataset,
                data: [
                  dataset.data.slice(0, 3).reduce((sum: number, val: number) => sum + val, 0),
                  dataset.data.slice(3, 6).reduce((sum: number, val: number) => sum + val, 0),
                  dataset.data.slice(6, 9).reduce((sum: number, val: number) => sum + val, 0),
                  dataset.data.slice(9, 12).reduce((sum: number, val: number) => sum + val, 0)
                ]
              }))
            };
          } else if (period === 'annually') {
            data = {
              ...data,
              labels: ['2024'],
              datasets: data.datasets.map((dataset: any) => ({
                ...dataset,
                data: [dataset.data.reduce((sum: number, val: number) => sum + val, 0)]
              }))
            };
          }
        }
        
        // Filter by category if needed
        if (category) {
          data = {
            ...data,
            datasets: data.datasets.filter((dataset: any) => dataset.label === category)
          };
        }
        
        await new Promise(resolve => setTimeout(resolve, 500));
      } else {
        data = await getSpendTrends(period, category);
      }
      
      setTrends(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch spend trends');
    } finally {
      setLoading(false);
    }
  }, [period, category]);

  useEffect(() => {
    fetchTrends();
  }, [fetchTrends]);

  return { trends, loading, error, refetch: fetchTrends };
}
