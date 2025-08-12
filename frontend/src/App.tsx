import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';
import api from './services/api';

function App() {
  const isAuthenticated = api.auth.isAuthenticated();

  const handleLogout = () => {
    api.auth.logout();
    window.location.href = '/login';
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        {/* Navigation - only show when authenticated */}
        {isAuthenticated && (
          <nav className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center space-x-8">
                  <h1 className="text-xl font-semibold text-gray-900">LAIT</h1>
                  <div className="flex space-x-4">
                    <Link 
                      to="/dashboard" 
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Dashboard
                    </Link>
                    <Link 
                      to="/upload" 
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Upload
                    </Link>
                  </div>
                </div>
                <div className="flex items-center">
                  <button
                    onClick={handleLogout}
                    className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium flex items-center"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </button>
                </div>
              </div>
            </div>
          </nav>
        )}
        
        {/* Routes */}
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/upload" element={
            <ProtectedRoute>
              <Upload />
            </ProtectedRoute>
          } />
          <Route path="/" element={
            isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
