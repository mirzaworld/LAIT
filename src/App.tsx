import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';
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

function AppContent() {
  return (
    <Router>
      <Routes>
        {/* Public landing page */}
        <Route path="/landing" element={<Landing />} />
        <Route path="/contact" element={<Contact />} />
        
        {/* Public auth routes */}
        <Route path="/login" element={<AuthRoute element={<Login />} />} />
        <Route path="/signup" element={<AuthRoute element={<SignUp />} />} />
        
        {/* Protected routes with layout */}
        <Route path="/" element={
          <ProtectedRoute element={
            <Layout>
              <Dashboard />
            </Layout>
          } />
        } />
        <Route path="/analytics" element={
          <ProtectedRoute element={
            <Layout>
              <Analytics />
            </Layout>
          } />
        } />
        <Route path="/analytics/advanced" element={
          <ProtectedRoute element={
            <Layout>
              <AdvancedAnalytics />
            </Layout>
          } />
        } />
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
        <Route path="/reports" element={
          <ProtectedRoute element={
            <Layout>
              <Reports />
            </Layout>
          } />
        } />
        <Route path="/settings" element={
          <ProtectedRoute element={
            <Layout>
              <Settings />
            </Layout>
          } />
        } />
        <Route path="/vendors" element={
          <ProtectedRoute element={
            <Layout>
              <VendorPerformance />
            </Layout>
          } />
        } />
        <Route path="/recommendations-alerts" element={
          <ProtectedRoute element={
            <Layout>
              <RecommendationsAlerts />
            </Layout>
          } />
        } />
        <Route path="/settings-integrations" element={
          <ProtectedRoute element={
            <Layout>
              <SettingsIntegrations />
            </Layout>
          } />
        } />
        <Route path="/legal-intelligence" element={
          <ProtectedRoute element={
            <Layout>
              <LegalIntelligence />
            </Layout>
          } />
        } />
        <Route path="/vendor-analytics" element={
          <ProtectedRoute element={
            <Layout>
              <VendorAnalyticsPage />
            </Layout>
          } />
        } />
        <Route path="/vendor-analytics/:id" element={
          <ProtectedRoute element={
            <Layout>
              <VendorAnalyticsPage />
            </Layout>
          } />
        } />
        <Route path="/diagnostics" element={
          <ProtectedRoute element={
            <Layout>
              <DiagnosticsPage />
            </Layout>
          } />
        } />
        
        {/* Catch-all route - redirect to landing if not authenticated, dashboard if authenticated */}
        <Route path="*" element={
          <ProtectedRoute element={<Navigate to="/" replace />} />
        } />
      </Routes>
    </Router>
  );
}

function App() {
  useEffect(() => {
    setDevelopmentToken();
  }, []);

  return (
    <AuthProvider>
      <NotificationProvider>
        <AppProvider>
          <AppContent />
        </AppProvider>
      </NotificationProvider>
    </AuthProvider>
  );
}

export default App;