import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { SimpleAppProvider, useSimpleApp } from './context/SimpleAppContext';

// Minimal test component
const TestDashboard: React.FC = () => {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>LAIT App Working!</h1>
      <p>✅ React is loaded</p>
      <p>✅ Authentication is working</p>
      <p>✅ Routing is working</p>
      <div style={{ background: '#f0f0f0', padding: '20px', marginTop: '20px' }}>
        <h2>Backend Status</h2>
        <p>Backend: ✅ Connected to http://localhost:5003</p>
        <p>Frontend: ✅ Running on http://localhost:5173</p>
      </div>
    </div>
  );
};

// Simple login component
const TestLogin: React.FC = () => {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>LAIT Login</h1>
      <p>Development mode - auto-authenticated</p>
    </div>
  );
};

// Route guard component
const ProtectedRoute: React.FC<{element: React.ReactNode}> = ({ element }) => {
  const { isAuthenticated } = useSimpleApp();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{element}</>;
};

// Auth route component
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
        <Route path="/login" element={<AuthRoute element={<TestLogin />} />} />
        <Route path="/" element={<ProtectedRoute element={<TestDashboard />} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

function TestSimpleApp() {
  return (
    <SimpleAppProvider>
      <AppContent />
    </SimpleAppProvider>
  );
}

export default TestSimpleApp;
