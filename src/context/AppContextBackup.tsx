// Backup of original AppContext for reference
import React, { createContext, useState, useContext, useEffect } from 'react';

interface AppContextType {
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (formData: SignUpForm) => Promise<boolean>;
  logout: () => void;
  darkMode: boolean;
  toggleDarkMode: () => void;
  googleSignIn: () => Promise<boolean>;
  phoneSignIn: (phoneNumber: string) => Promise<string>;
  verifyPhoneCode: (verificationId: string, code: string) => Promise<boolean>;
  userProfile: UserProfile | null;
  updateUserProfile: (updates: Partial<UserProfile>) => Promise<boolean>;
}

interface UserProfile {
  uid: string;
  prefix: string;
  firstName: string;
  middleName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  organizationType: string;
  termsAccepted: boolean;
  phoneVerified: boolean;
  createdAt: Date;
  updatedAt: Date;
}

interface SignUpForm {
  prefix: string;
  firstName: string;
  middleName: string;
  lastName: string;
  email: string;
  password: string;
  phone: string;
  dateOfBirth: string;
  organizationType: string;
  termsAccepted: boolean;
}

const defaultContextValue: AppContextType = {
  isAuthenticated: false,
  login: async () => false,
  signup: async () => false,
  logout: () => {},
  darkMode: false,
  toggleDarkMode: () => {},
  googleSignIn: async () => false,
  phoneSignIn: async () => '',
  verifyPhoneCode: async () => false,
  userProfile: null,
  updateUserProfile: async () => false,
};

export const AppContext = createContext<AppContextType>(defaultContextValue);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

  // Check for stored authentication
  useEffect(() => {
    const token = localStorage.getItem('lait_token') || localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
      // Set mock user profile for development
      const mockProfile: UserProfile = {
        uid: 'dev-user-1',
        prefix: 'Mr.',
        firstName: 'John',
        middleName: 'Legal',
        lastName: 'Demo',
        email: 'admin@lait.demo',
        phone: '+1-555-0123',
        dateOfBirth: '1980-01-01',
        organizationType: 'Law Firm',
        termsAccepted: true,
        phoneVerified: true,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      setUserProfile(mockProfile);
    }
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    // For development, accept any valid credentials
    if (email && password) {
      const mockToken = 'mock-jwt-token-for-development';
      localStorage.setItem('lait_token', mockToken);
      setIsAuthenticated(true);
      
      const mockProfile: UserProfile = {
        uid: 'dev-user-1',
        prefix: 'Mr.',
        firstName: 'John',
        middleName: 'Legal',
        lastName: 'Demo',
        email: email,
        phone: '+1-555-0123',
        dateOfBirth: '1980-01-01',
        organizationType: 'Law Firm',
        termsAccepted: true,
        phoneVerified: true,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      setUserProfile(mockProfile);
      return true;
    }
    return false;
  };

  const signup = async (formData: SignUpForm): Promise<boolean> => {
    // For development, accept any signup
    const mockToken = 'mock-jwt-token-for-development';
    localStorage.setItem('lait_token', mockToken);
    setIsAuthenticated(true);
    
    const profile: UserProfile = {
      uid: 'dev-user-1',
      prefix: formData.prefix,
      firstName: formData.firstName,
      middleName: formData.middleName,
      lastName: formData.lastName,
      email: formData.email,
      phone: formData.phone,
      dateOfBirth: formData.dateOfBirth,
      organizationType: formData.organizationType,
      termsAccepted: formData.termsAccepted,
      phoneVerified: false,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    setUserProfile(profile);
    return true;
  };

  const logout = () => {
    localStorage.removeItem('lait_token');
    localStorage.removeItem('token');
    localStorage.removeItem('authToken');
    setIsAuthenticated(false);
    setUserProfile(null);
  };

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('darkMode', newDarkMode.toString());
  };

  const googleSignIn = async (): Promise<boolean> => {
    // Mock Google sign in for development
    return login('google@lait.demo', 'google123');
  };

  const phoneSignIn = async (phoneNumber: string): Promise<string> => {
    // Mock phone sign in for development
    return 'mock-verification-id';
  };

  const verifyPhoneCode = async (verificationId: string, code: string): Promise<boolean> => {
    // Mock phone verification for development
    return code === '123456';
  };

  const updateUserProfile = async (updates: Partial<UserProfile>): Promise<boolean> => {
    if (userProfile) {
      setUserProfile({ ...userProfile, ...updates, updatedAt: new Date() });
      return true;
    }
    return false;
  };

  return (
    <AppContext.Provider
      value={{
        isAuthenticated,
        login,
        signup,
        logout,
        darkMode,
        toggleDarkMode,
        googleSignIn,
        phoneSignIn,
        verifyPhoneCode,
        userProfile,
        updateUserProfile,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
