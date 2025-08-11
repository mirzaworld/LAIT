import React, { createContext, useState, useContext, useEffect } from 'react';
import { login as apiLogin, register as apiRegister } from '../services/api';

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (userData: RegisterData) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
}

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  company?: string;
}

interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  company?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check for existing token on app start
  useEffect(() => {
    const token = localStorage.getItem('lait_token');
    if (token && token !== 'mock-jwt-token-for-development') {
      // TODO: Validate token with backend and get user info
      setIsAuthenticated(true);
      // For now, we'll just set authenticated state
      // In a complete implementation, we'd call /api/auth/profile to get user data
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      console.log('🔐 Attempting login with backend API...');
      const response = await apiLogin(email, password);
      
      if (response.token && response.user) {
        localStorage.setItem('lait_token', response.token);
        setUser(response.user);
        setIsAuthenticated(true);
        console.log('✅ Login successful!');
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('❌ Login failed:', error);
      return false;
    }
  };

  const register = async (userData: RegisterData): Promise<boolean> => {
    try {
      console.log('📝 Attempting registration with backend API...');
      const response = await apiRegister(userData);
      
      if (response.user_id) {
        console.log('✅ Registration successful!');
        // After registration, user typically needs to verify email
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('❌ Registration failed:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('lait_token');
    setUser(null);
    setIsAuthenticated(false);
    console.log('👋 Logged out');
  };

  const value = {
    isAuthenticated,
    user,
    login,
    register,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
