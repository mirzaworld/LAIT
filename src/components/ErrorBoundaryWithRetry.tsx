import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
  retryCount: number;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error?: Error; retry: () => void }>;
  maxRetries?: number;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

class ErrorBoundaryWithRetry extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      retryCount: 0
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({ errorInfo });
    
    // Log error to console and notify error monitoring service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Call onError prop if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleRetry = () => {
    const { maxRetries = 3 } = this.props;
    
    if (this.state.retryCount < maxRetries) {
      this.setState(state => ({
        hasError: false,
        error: undefined,
        errorInfo: undefined,
        retryCount: state.retryCount + 1
      }));
    } else {
      console.error('Max retries reached, please refresh the page');
    }
  };

  render() {
    const { hasError, error, retryCount } = this.state;
    const { maxRetries = 3 } = this.props;

    if (hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;
      return (
        <FallbackComponent 
          error={error} 
          retry={retryCount < maxRetries ? this.handleRetry : undefined} 
        />
      );
    }

    return this.props.children;
  }
}

interface DefaultErrorFallbackProps {
  error?: Error;
  retry?: () => void;
}

const DefaultErrorFallback: React.FC<DefaultErrorFallbackProps> = ({ error, retry }) => (
  <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
    <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
    <h3 className="text-lg font-semibold text-red-800 mb-2">Something went wrong</h3>
    <p className="text-red-600 mb-4">
      {error?.message || 'An unexpected error occurred while loading this component.'}
    </p>
    {retry ? (
      <button
        onClick={retry}
        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors inline-flex items-center"
      >
        <RefreshCw className="w-4 h-4 mr-2" />
        Retry
      </button>
    ) : (
      <button
        onClick={() => window.location.reload()}
        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
      >
        Reload Page
      </button>
    )}
  </div>
);

export default ErrorBoundaryWithRetry;
