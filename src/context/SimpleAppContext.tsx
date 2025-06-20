import React, { createContext, useState, useContext, useEffect } from 'react';

interface SimpleAppContextType {
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  user: any;
  darkMode: boolean;
  toggleDarkMode: () => void;
}

const SimpleAppContext = createContext<SimpleAppContextType | undefined>(undefined);

export const SimpleAppProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    // For development, check if we have a token or auto-authenticate
    const token = localStorage.getItem('lait_token');
    return !!token;
  });
  const [user, setUser] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('lait_token');
    const userData = localStorage.getItem('lait_user');
    
    if (token && userData) {
      setIsAuthenticated(true);
      setUser(JSON.parse(userData));
    } else if (!token) {
      // For development, set a mock token if none exists
      console.log('Setting development token for LAIT demo');
      localStorage.setItem('lait_token', 'mock-jwt-token-for-development');
      localStorage.setItem('lait_user', JSON.stringify({ 
        id: '1', 
        email: 'demo@lait.com', 
        name: 'Demo User' 
      }));
      setIsAuthenticated(true);
      setUser({ id: '1', email: 'demo@lait.com', name: 'Demo User' });
    }
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      console.log('Attempting login with:', email);
      
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Login successful:', data);
        
        // Store token and user data
        localStorage.setItem('lait_token', data.token);
        localStorage.setItem('lait_user', JSON.stringify(data.user));
        
        setIsAuthenticated(true);
        setUser(data.user);
        return true;
      } else {
        console.error('Login failed:', response.status);
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('lait_token');
    localStorage.removeItem('lait_user');
    setIsAuthenticated(false);
    setUser(null);
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <SimpleAppContext.Provider value={{
      isAuthenticated,
      login,
      logout,
      user,
      darkMode,
      toggleDarkMode
    }}>
      {children}
    </SimpleAppContext.Provider>
  );
};

export const useSimpleApp = () => {
  const context = useContext(SimpleAppContext);
  if (context === undefined) {
    throw new Error('useSimpleApp must be used within a SimpleAppProvider');
  }
  return context;
};
