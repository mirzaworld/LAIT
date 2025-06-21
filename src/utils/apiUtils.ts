import axios, { AxiosError, AxiosResponse } from 'axios';

// Error tracking metrics
const errorMetrics = {
  totalErrors: 0,
  retryAttempts: 0,
  errorsByEndpoint: new Map<string, number>(),
  errorsByType: new Map<string, number>()
};

interface RetryConfig {
  maxRetries?: number;
  retryDelay?: number;
  shouldRetry?: (error: AxiosError) => boolean;
}

// Enhanced retry configuration
const defaultRetryConfig: Required<RetryConfig> = {
  maxRetries: 3,
  retryDelay: 1000,
  shouldRetry: (error: AxiosError) => {
    // Retry on network errors, 5xx errors, and specific 4xx errors
    const shouldRetry = !error.response ||
      error.response.status >= 500 ||
      error.response.status === 429; // Rate limit

    if (shouldRetry) {
      const endpoint = error.config?.url || 'unknown';
      errorMetrics.errorsByEndpoint.set(
        endpoint,
        (errorMetrics.errorsByEndpoint.get(endpoint) || 0) + 1
      );
      
      const errorType = error.response?.status?.toString() || 'network';
      errorMetrics.errorsByType.set(
        errorType,
        (errorMetrics.errorsByType.get(errorType) || 0) + 1
      );
    }

    return shouldRetry;
  }
};

export const withRetry = async <T>(
  apiCall: () => Promise<T>,
  config: RetryConfig = {}
): Promise<T> => {
  const finalConfig = { ...defaultRetryConfig, ...config };
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt < finalConfig.maxRetries; attempt++) {
    try {
      const result = await apiCall();
      // Log successful retry if it wasn't the first attempt
      if (attempt > 0) {
        console.log(`API call succeeded after ${attempt + 1} attempts`);
      }
      return result;
    } catch (error: any) {
      lastError = error;
      const isAxiosError = axios.isAxiosError(error);
      
      // Log the error with relevant details
      console.error(`API Error (Attempt ${attempt + 1}/${finalConfig.maxRetries}):`, {
        endpoint: isAxiosError ? error.config?.url : 'unknown',
        method: isAxiosError ? error.config?.method : 'unknown',
        status: isAxiosError ? error.response?.status : 'unknown',
        error: error.message
      });

      // Check if we should retry
      if (
        attempt < finalConfig.maxRetries - 1 &&
        (!isAxiosError || finalConfig.shouldRetry(error))
      ) {
        await new Promise(resolve => setTimeout(resolve, finalConfig.retryDelay));
        continue;
      }
      break;
    }
  }

  throw lastError;
};

// API Error monitoring and logging
// API Health Check
export let isApiHealthy = true;
let lastHealthCheck = 0;
const HEALTH_CHECK_INTERVAL = 30000; // 30 seconds

export const checkApiHealth = async () => {
  try {
    const now = Date.now();
    if (now - lastHealthCheck < HEALTH_CHECK_INTERVAL) {
      return isApiHealthy;
    }

    lastHealthCheck = now;
    const response = await axios.get('/api/health');
    isApiHealthy = response.status === 200;
    
    if (!isApiHealthy) {
      console.error('API Health Check Failed:', response.status);
    }
    
    return isApiHealthy;
  } catch (error) {
    console.error('API Health Check Error:', error);
    isApiHealthy = false;
    return false;
  }
};

// Enhanced setupAPIMonitoring
export const setupAPIMonitoring = () => {
  // Add request interceptor
  axios.interceptors.request.use(
    async (config) => {
      if (!isApiHealthy && config.url !== '/api/health') {
        // Check health before making request
        const healthy = await checkApiHealth();
        if (!healthy) {
          throw new Error('API is currently unavailable');
        }
      }
      
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] API Request:`, {
        url: config.url,
        method: config.method,
        params: config.params
      });
      
      // Add request ID for tracking
      config.headers['X-Request-ID'] = crypto.randomUUID();
      
      return config;
    },
    error => {
      console.error('API Request Error:', error);
      return Promise.reject(error);
    }
  );

  // Add response interceptor
  axios.interceptors.response.use(
    (response: AxiosResponse) => {
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] API Response:`, {
        url: response.config.url,
        status: response.status,
        duration: response.headers['x-response-time'],
        requestId: response.config.headers['X-Request-ID']
      });
      return response;
    },
    async (error: AxiosError) => {
      const timestamp = new Date().toISOString();
      errorMetrics.totalErrors++;
      
      console.error(`[${timestamp}] API Error:`, {
        url: error.config?.url,
        status: error.response?.status,
        message: error.message,
        requestId: error.config?.headers['X-Request-ID']
      });

      // Check if it's a server error and update health status
      if (error.response?.status && error.response.status >= 500) {
        isApiHealthy = false;
        // Trigger immediate health check
        checkApiHealth();
      }

      return Promise.reject(error);
    }
  );

  // Start periodic health checks
  setInterval(checkApiHealth, HEALTH_CHECK_INTERVAL);
};

// Fallback data type for caching
export interface FallbackData<T> {
  data: T;
  timestamp: number;
  expiresIn: number;
}

// Utility to manage fallback data in localStorage
export const fallbackDataManager = {
  set: <T>(key: string, data: T, expiresIn: number = 3600000) => {
    const fallbackData: FallbackData<T> = {
      data,
      timestamp: Date.now(),
      expiresIn
    };
    localStorage.setItem(`fallback_${key}`, JSON.stringify(fallbackData));
  },
  
  get: <T>(key: string): T | null => {
    const stored = localStorage.getItem(`fallback_${key}`);
    if (!stored) return null;
    
    const fallbackData: FallbackData<T> = JSON.parse(stored);
    const isExpired = Date.now() - fallbackData.timestamp > fallbackData.expiresIn;
    
    return isExpired ? null : fallbackData.data;
  },
  
  clear: (key: string) => {
    localStorage.removeItem(`fallback_${key}`);
  }
};
