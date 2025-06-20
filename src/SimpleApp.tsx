import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { SimpleAppProvider, useSimpleApp } from './context/SimpleAppContext';
import SimpleLayout from './components/SimpleLayout';
import SimpleDashboard from './pages/SimpleDashboard';
import Analytics from './pages/Analytics';
import Invoices from './pages/Invoices';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import SimpleLogin from './pages/SimpleLogin';
import 'react-toastify/dist/ReactToastify.css';

// Route guard component to handle authentication
const ProtectedRoute: React.FC<{element: React.ReactNode}> = ({ element }) => {
  const { isAuthenticated } = useSimpleApp();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{element}</>;
};

// Auth route component to prevent authenticated users from accessing login
const AuthRoute: React.FC<{element: React.ReactNode}> = ({ element }) => {
  const { isAuthenticated } = useSimpleApp();
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return <>{element}</>;
};

function AppContent() {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<AuthRoute element={<SimpleLogin />} />} />
        
        {/* Protected routes */}
        <Route path="/" element={<ProtectedRoute element={<SimpleLayout />} />}>
          <Route index element={<SimpleDashboard />} />
          <Route path="dashboard" element={<SimpleDashboard />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="invoices" element={<Invoices />} />
          <Route path="reports" element={<Reports />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        
        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

function App() {
  console.log('App component rendered');
  
  return (
    <SimpleAppProvider>
      <AppContent />
    </SimpleAppProvider>
  );
}

export default App;
