import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';
import { setupAPIMonitoring } from './utils/apiUtils';
import ErrorBoundaryWithRetry from './components/ErrorBoundaryWithRetry';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import UnifiedAnalytics from './pages/UnifiedAnalytics';
import Invoices from './pages/Invoices';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import Landing from './pages/Landing';
import Contact from './pages/Contact';
import UploadInvoice from './pages/UploadInvoice';
import InvoiceList from './pages/InvoiceList';
import VendorPerformance from './pages/VendorPerformance';
import RecommendationsAlerts from './pages/RecommendationsAlerts';
import LegalIntelligence from './pages/LegalIntelligence';
import DiagnosticsPage from './pages/DiagnosticsPage';
import SettingsIntegrations from './pages/SettingsIntegrations';
import VendorAnalyticsPage from './pages/VendorAnalyticsPage';
import { AppProvider, useApp } from './context/AppContext';
import 'react-toastify/dist/ReactToastify.css';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

// Set mock token for development and auto-authenticate
const setDevelopmentToken = () => {
  if (!localStorage.getItem('lait_token') && !localStorage.getItem('token')) {
    console.log('Setting development token for LAIT demo');
    localStorage.setItem('lait_token', 'mock-jwt-token-for-development');
    
    // Also trigger a state update by dispatching a storage event
    window.dispatchEvent(new Event('storage'));
  }
};

// Route guard component to handle authentication
const ProtectedRoute: React.FC<{element: React.ReactNode}> = ({ element }) => {
  const { isAuthenticated } = useApp();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{element}</>;
};

// Auth route component to prevent authenticated users from accessing login/signup
const AuthRoute: React.FC<{element: React.ReactNode}> = ({ element }) => {
  const { isAuthenticated } = useApp();
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return <>{element}</>;
};

// Home route component to redirect authenticated users to dashboard
const HomeRoute: React.FC = () => {
  const { isAuthenticated } = useApp();
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return <Landing />;
};

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Enhanced error logging
const logError = (error: Error, errorInfo: React.ErrorInfo) => {
  console.error('Application Error:', error);
  console.error('Error Details:', errorInfo);
  // You can add your error reporting service here
};

// Root App Component
const AppContent = () => {
  useEffect(() => {
    // Initialize API monitoring
    setupAPIMonitoring();
    
    // Set development token if needed
    setDevelopmentToken();
    
    // Add error event listener for unhandled errors
    const handleError = (event: ErrorEvent) => {
      console.error('Unhandled error:', event.error);
      event.preventDefault();
    };
    
    window.addEventListener('error', handleError);
    
    // Add unhandled promise rejection handler
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error('Unhandled promise rejection:', event.reason);
      event.preventDefault();
    };
    
    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    
    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundaryWithRetry
        maxRetries={3}
        onError={logError}
        fallback={({ error, retry }) => (
          <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="max-w-md w-full space-y-8 p-8 bg-white shadow-lg rounded-lg">
              <h2 className="text-2xl font-bold text-center text-gray-900">
                Something went wrong
              </h2>
              <p className="text-gray-600 text-center">
                {error?.message || 'An unexpected error occurred'}
              </p>
              <div className="flex justify-center">
                <button
                  onClick={retry}
                  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        )}
      >
        <NotificationProvider>
          <AuthProvider>
            <AppProvider>
              <Router>
                <div className="min-h-screen bg-gray-50">
                  <Routes>
                    {/* Public Routes */}
                    <Route path="/" element={<HomeRoute />} />
                    <Route path="/landing" element={<Landing />} />
                    <Route path="/login" element={<AuthRoute element={<Login />} />} />
                    <Route path="/signup" element={<AuthRoute element={<SignUp />} />} />
                    <Route path="/contact" element={<Contact />} />
                    
                    {/* Protected Routes */}
                    <Route path="/dashboard" element={
                      <ProtectedRoute element={
                        <Layout>
                          <Dashboard />
                        </Layout>
                      } />
                    } />
                    
                    {/* Analytics Route */}
                    <Route path="/analytics" element={
                      <ProtectedRoute element={
                        <Layout>
                          <UnifiedAnalytics />
                        </Layout>
                      } />
                    } />
                    <Route path="/analytics/:type" element={
                      <ProtectedRoute element={
                        <Layout>
                          <UnifiedAnalytics />
                        </Layout>
                      } />
                    } />
                    
                    {/* Legal Intelligence */}
                    <Route path="/legal-intelligence" element={
                      <ProtectedRoute element={
                        <Layout>
                          <LegalIntelligence />
                        </Layout>
                      } />
                    } />
                    
                    {/* Invoice Management */}
                    <Route path="/invoices" element={
                      <ProtectedRoute element={
                        <Layout>
                          <Invoices />
                        </Layout>
                      } />
                    } />
                    <Route path="/invoices/:id" element={
                      <ProtectedRoute element={
                        <Layout>
                          <Invoices />
                        </Layout>
                      } />
                    } />
                    <Route path="/invoices/upload" element={
                      <ProtectedRoute element={
                        <Layout>
                          <UploadInvoice />
                        </Layout>
                      } />
                    } />
                    <Route path="/invoices/list" element={
                      <ProtectedRoute element={
                        <Layout>
                          <InvoiceList />
                        </Layout>
                      } />
                    } />
                    
                    {/* Reports */}
                    <Route path="/reports" element={
                      <ProtectedRoute element={
                        <Layout>
                          <Reports />
                        </Layout>
                      } />
                    } />
                    
                    {/* Settings */}
                    <Route path="/settings" element={
                      <ProtectedRoute element={
                        <Layout>
                          <Settings />
                        </Layout>
                      } />
                    } />
                    
                    {/* Diagnostics */}
                    <Route path="/diagnostics" element={
                      <ProtectedRoute element={
                        <Layout>
                          <DiagnosticsPage />
                        </Layout>
                      } />
                    } />
                    
                    {/* Catch all route */}
                    <Route path="*" element={<ProtectedRoute element={<Navigate to="/dashboard" replace />} />} />
                  </Routes>
                  
                  {/* Global Toaster */}
                  <Toaster
                    position="top-right"
                    toastOptions={{
                      duration: 4000,
                      style: {
                        background: '#363636',
                        color: '#fff',
                      },
                      success: {
                        duration: 3000,
                        iconTheme: {
                          primary: '#10B981',
                          secondary: '#fff',
                        },
                      },
                      error: {
                        duration: 5000,
                        iconTheme: {
                          primary: '#EF4444',
                          secondary: '#fff',
                        },
                      },
                    }}
                  />
                </div>
              </Router>
            </AppProvider>
          </AuthProvider>
        </NotificationProvider>
      </ErrorBoundaryWithRetry>
    </QueryClientProvider>
  );
};

const App = () => {
  return <AppContent />;
};

export default App;