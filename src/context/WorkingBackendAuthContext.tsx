import React, { createContext, useState, useContext, useEffect } from 'react';

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
    const checkAuth = async () => {
      const token = localStorage.getItem('lait_token');
      if (token && token !== 'mock-jwt-token-for-development') {
        try {
          const response = await fetch('/api/auth/me', {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (response.ok) {
            const userData = await response.json();
            setUser({
              id: userData.id.toString(),
              email: userData.email,
              first_name: userData.first_name,
              last_name: userData.last_name,
              role: userData.role,
              company: userData.company
            });
            setIsAuthenticated(true);
            console.log('✅ Authentication restored from token');
          } else {
            console.log('🔑 Token invalid, removing...');
            localStorage.removeItem('lait_token');
          }
        } catch (error) {
          console.error('❌ Auth check failed:', error);
          localStorage.removeItem('lait_token');
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      console.log('🔐 Attempting login:', email);
      
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('lait_token', data.token);
        setUser({
          id: data.user.id.toString(),
          email: data.user.email,
          first_name: data.user.first_name,
          last_name: data.user.last_name,
          role: data.user.role,
          company: data.user.company
        });
        setIsAuthenticated(true);
        console.log('✅ Login successful!');
        return true;
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ Login failed:', errorData.error || 'Unknown error');
        return false;
      }
    } catch (error) {
      console.error('❌ Login error:', error);
      return false;
    }
  };

  const register = async (userData: RegisterData): Promise<boolean> => {
    try {
      console.log('📝 Attempting registration:', userData.email);
      
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('lait_token', data.token);
        setUser({
          id: data.user.id.toString(),
          email: data.user.email,
          first_name: data.user.first_name,
          last_name: data.user.last_name,
          role: data.user.role,
          company: data.user.company
        });
        setIsAuthenticated(true);
        console.log('✅ Registration successful!');
        return true;
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ Registration failed:', errorData.error || 'Unknown error');
        return false;
      }
    } catch (error) {
      console.error('❌ Registration error:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('lait_token');
    setUser(null);
    setIsAuthenticated(false);
    console.log('👋 Logged out');
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        login,
        register,
        logout,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
