import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';
import { setupAPIMonitoring } from './utils/apiUtils';
import ErrorBoundaryWithRetry from './components/ErrorBoundaryWithRetry';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import AdvancedAnalytics from './pages/AdvancedAnalytics';
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
    return <Navigate to="/" replace />;
  }
  
  return <>{element}</>;
};

// Add future flags configuration
const router = createBrowserRouter(
  [
    // Public landing page
    { path: "/landing", element: <Landing /> },
    { path: "/contact", element: <Contact /> },
    
    // Public auth routes
    { path: "/login", element: <AuthRoute element={<Login />} /> },
    { path: "/signup", element: <AuthRoute element={<SignUp />} /> },
    
    // Protected routes with layout
    { path: "/", element: 
      <ProtectedRoute element={
        <Layout>
          <Dashboard />
        </Layout>
      } />
    },
    { path: "/analytics", element: 
      <ProtectedRoute element={
        <Layout>
          <Analytics />
        </Layout>
      } />
    },
    { path: "/analytics/advanced", element: 
      <ProtectedRoute element={
        <Layout>
          <AdvancedAnalytics />
        </Layout>
      } />
    },
    { path: "/invoices", element: 
      <ProtectedRoute element={
        <Layout>
          <Invoices />
        </Layout>
      } />
    },
    { path: "/invoices/:id", element: 
      <ProtectedRoute element={
        <Layout>
          <Invoices />
        </Layout>
      } />
    },
    { path: "/invoices/upload", element: 
      <ProtectedRoute element={
        <Layout>
          <UploadInvoice />
        </Layout>
      } />
    },
    { path: "/invoices/list", element: 
      <ProtectedRoute element={
        <Layout>
          <InvoiceList />
        </Layout>
      } />
    },
    { path: "/reports", element: 
      <ProtectedRoute element={
        <Layout>
          <Reports />
        </Layout>
      } />
    },
    { path: "/settings", element: 
      <ProtectedRoute element={
        <Layout>
          <Settings />
        </Layout>
      } />
    },
    { path: "/vendors", element: 
      <ProtectedRoute element={
        <Layout>
          <VendorPerformance />
        </Layout>
      } />
    },
    { path: "/recommendations-alerts", element: 
      <ProtectedRoute element={
        <Layout>
          <RecommendationsAlerts />
        </Layout>
      } />
    },
    { path: "/settings-integrations", element: 
      <ProtectedRoute element={
        <Layout>
          <SettingsIntegrations />
        </Layout>
      } />
    },
    { path: "/legal-intelligence", element: 
      <ProtectedRoute element={
        <Layout>
          <LegalIntelligence />
        </Layout>
      } />
    },
    { path: "/vendor-analytics", element: 
      <ProtectedRoute element={
        <Layout>
          <VendorAnalyticsPage />
        </Layout>
      } />
    },
    { path: "/vendor-analytics/:id", element: 
      <ProtectedRoute element={
        <Layout>
          <VendorAnalyticsPage />
        </Layout>
      } />
    },
    { path: "/diagnostics", element: 
      <ProtectedRoute element={
        <Layout>
          <DiagnosticsPage />
        </Layout>
      } />
    },
    
    // Catch-all route - redirect to landing if not authenticated, dashboard if authenticated
    { path: "*", element: 
      <ProtectedRoute element={<Navigate to="/" replace />} />
    }
  ],
  {
    future: {
      // v7_startTransition: true,
      v7_relativeSplatPath: true
    }
  }
);

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
            <RouterProvider router={router} />
          </AppProvider>
        </AuthProvider>
      </NotificationProvider>
    </ErrorBoundaryWithRetry>
  );
};

const App = () => {
  return <AppContent />;
};

export default App;