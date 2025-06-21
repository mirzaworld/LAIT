# API Error Handling and Fallback Documentation

## API Retry Mechanism

The application uses a robust retry mechanism for handling API failures. This is implemented in `src/utils/apiUtils.ts`.

### Usage:

```typescript
import { withRetry } from '../utils/apiUtils';

// Example usage in an API call
const fetchData = async () => {
  return withRetry(
    () => axios.get('/api/data'),
    {
      maxRetries: 3,
      retryDelay: 1000,
      shouldRetry: (error) => error.response?.status >= 500
    }
  );
};
```

### Configuration Options:

- `maxRetries`: Maximum number of retry attempts (default: 3)
- `retryDelay`: Delay between retries in milliseconds (default: 1000)
- `shouldRetry`: Function to determine if a particular error should trigger a retry

## Error Boundaries

The application uses enhanced error boundaries with retry capabilities. This is implemented in `src/components/ErrorBoundaryWithRetry.tsx`.

### Usage:

```tsx
import ErrorBoundaryWithRetry from '../components/ErrorBoundaryWithRetry';

const MyComponent = () => {
  return (
    <ErrorBoundaryWithRetry
      maxRetries={3}
      onError={(error, errorInfo) => {
        // Custom error handling
        console.error('Component Error:', error);
      }}
    >
      <MyContent />
    </ErrorBoundaryWithRetry>
  );
};
```

## Fallback Data Mechanism

The application implements a local storage-based fallback mechanism for handling offline scenarios or API failures.

### Usage:

```typescript
import { fallbackDataManager } from '../utils/apiUtils';

// Storing fallback data
fallbackDataManager.set('dashboard-metrics', dashboardData, 3600000); // 1 hour expiry

// Retrieving fallback data
const fallbackData = fallbackDataManager.get('dashboard-metrics');

// Example implementation in a hook
const useDashboardData = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Try to fetch fresh data
        const response = await withRetry(() => axios.get('/api/dashboard'));
        setData(response.data);
        // Store as fallback
        fallbackDataManager.set('dashboard-metrics', response.data);
      } catch (error) {
        // Try to get fallback data
        const fallback = fallbackDataManager.get('dashboard-metrics');
        if (fallback) {
          setData(fallback);
          console.log('Using fallback dashboard data');
        }
      }
    };
    
    fetchData();
  }, []);
  
  return data;
};
```

## API Error Monitoring

The application includes built-in API monitoring and logging:

- All API requests and responses are logged with timestamps
- Response times are tracked
- Errors are logged with detailed information
- Custom monitoring can be added via the error handlers

### Monitoring Setup:

```typescript
import { setupAPIMonitoring } from '../utils/apiUtils';

// Call this during app initialization
setupAPIMonitoring();
```

## Best Practices

1. Always wrap data-fetching components in error boundaries
2. Use the retry mechanism for important API calls
3. Implement fallback data for critical features
4. Log errors appropriately for debugging
5. Consider the user experience when handling errors
6. Keep fallback data up to date
7. Clear expired fallback data

## Error Types and Handling

1. Network Errors
   - Automatically retried
   - Fallback to cached data if available
   
2. Server Errors (5xx)
   - Automatically retried
   - Logged for monitoring
   - Show user-friendly error message
   
3. Client Errors (4xx)
   - Not retried (except 429)
   - Clear error messages to users
   
4. Validation Errors
   - Handled at form level
   - Clear feedback to users

## Monitoring and Debugging

All API errors are automatically logged with:
- Timestamp
- URL
- Method
- Status code
- Error message
- Request duration
- Request/Response data (sanitized)

## Development Guidelines

1. Always handle loading, error, and success states
2. Implement retry logic for network-dependent features
3. Provide fallback UI for error states
4. Log errors appropriately
5. Keep fallback data updated
6. Clean up expired fallback data
7. Test error scenarios
