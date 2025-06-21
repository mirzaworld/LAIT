import { isApiHealthy } from './apiUtils';

class FallbackDataService {
  private storage: Storage = localStorage;
  private prefix: string = 'lait_fallback_';
  private ttl: number = 1000 * 60 * 60; // 1 hour default TTL

  constructor(ttl?: number) {
    if (ttl) {
      this.ttl = ttl;
    }
  }

  // Store fallback data with TTL
  async set(key: string, data: any): Promise<void> {
    const item = {
      data,
      timestamp: Date.now(),
    };
    try {
      await this.storage.setItem(this.prefix + key, JSON.stringify(item));
    } catch (error) {
      console.error('Error storing fallback data:', error);
    }
  }

  // Get fallback data if it's still valid
  async get<T>(key: string): Promise<T | null> {
    try {
      const item = await this.storage.getItem(this.prefix + key);
      if (!item) return null;

      const { data, timestamp } = JSON.parse(item);
      const age = Date.now() - timestamp;

      // Return null if data is expired
      if (age > this.ttl) {
        await this.remove(key);
        return null;
      }

      return data as T;
    } catch (error) {
      console.error('Error retrieving fallback data:', error);
      return null;
    }
  }

  // Remove fallback data
  async remove(key: string): Promise<void> {
    try {
      await this.storage.removeItem(this.prefix + key);
    } catch (error) {
      console.error('Error removing fallback data:', error);
    }
  }

  // Clear all fallback data
  async clear(): Promise<void> {
    try {
      const keys = Object.keys(this.storage).filter(key => key.startsWith(this.prefix));
      await Promise.all(keys.map(key => this.storage.removeItem(key)));
    } catch (error) {
      console.error('Error clearing fallback data:', error);
    }
  }

  // Get all stored fallback data keys
  async getKeys(): Promise<string[]> {
    try {
      return Object.keys(this.storage)
        .filter(key => key.startsWith(this.prefix))
        .map(key => key.replace(this.prefix, ''));
    } catch (error) {
      console.error('Error getting fallback data keys:', error);
      return [];
    }
  }

  // Check if fallback data exists and is valid
  async has(key: string): Promise<boolean> {
    const data = await this.get(key);
    return data !== null;
  }
}

// Create and export a singleton instance
export const fallbackDataService = new FallbackDataService();

// Helper hook for React components
export const useFallbackData = <T>(key: string, fetchData: () => Promise<T>) => {
  const getFallbackData = async (): Promise<T | null> => {
    try {
      // Try to get fresh data if API is healthy
      if (isApiHealthy) {
        const data = await fetchData();
        // Store for fallback
        await fallbackDataService.set(key, data);
        return data;
      }

      // Use fallback data if API is unhealthy
      return await fallbackDataService.get<T>(key);
    } catch (error) {
      console.error('Error in useFallbackData:', error);
      // Try fallback as last resort
      return await fallbackDataService.get<T>(key);
    }
  };

  return { getFallbackData };
};
