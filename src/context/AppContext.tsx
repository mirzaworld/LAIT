import React, { createContext, useState, useContext, useEffect } from 'react';
import { 
  GoogleAuthProvider, 
  signInWithPopup, 
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  updateProfile,
  PhoneAuthProvider,
  RecaptchaVerifier,
  signInWithPhoneNumber,
  linkWithCredential
} from 'firebase/auth';
import { auth, storeUserProfile, getUserProfile } from '../services/firebase';

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
  updateUserProfile: (profile: Partial<UserProfile>) => Promise<boolean>;
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
  phoneVerified?: boolean;
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

export const AppProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!auth.currentUser;
  });
  
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  
  const [darkMode, setDarkMode] = useState(() => {
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return localStorage.getItem('darkMode') 
      ? localStorage.getItem('darkMode') === 'true'
      : systemPrefersDark;
  });

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      if (localStorage.getItem('darkMode') === null) {
        setDarkMode(e.matches);
      }
    };
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      document.body.classList.add('dark:bg-gray-900');
    } else {
      document.documentElement.classList.remove('dark');
      document.body.classList.remove('dark:bg-gray-900');
    }
  }, [darkMode]);

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      if (user) {
        const profile = await getUserProfile(user.uid);
        if (profile) {
          setUserProfile({ ...profile, uid: user.uid } as UserProfile);
        }
      } else {
        setUserProfile(null);
      }
    });
    return () => unsubscribe();
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const token = await userCredential.user.getIdToken();
      localStorage.setItem('authToken', token);
      setIsAuthenticated(true);
      
      // Load user profile
      const profile = await getUserProfile(userCredential.user.uid);
      if (profile) {
        setUserProfile({ ...profile, uid: userCredential.user.uid } as UserProfile);
      }
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const signup = async (formData: SignUpForm): Promise<boolean> => {
    try {
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        formData.email,
        formData.password
      );
      
      // Add display name to auth profile
      await updateProfile(userCredential.user, {
        displayName: `${formData.prefix} ${formData.firstName} ${formData.lastName}`,
      });
      
      // Store complete profile in Firestore
      const profile: Omit<UserProfile, 'uid'> = {
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
      
      await storeUserProfile(userCredential.user.uid, profile);
      
      const token = await userCredential.user.getIdToken();
      localStorage.setItem('authToken', token);
      setIsAuthenticated(true);
      setUserProfile({ ...profile, uid: userCredential.user.uid });
      
      return true;
    } catch (error) {
      console.error('Signup error:', error);
      return false;
    }
  };

  const phoneSignIn = async (phoneNumber: string): Promise<string> => {
    try {
      // Initialize recaptcha
      const recaptchaVerifier = new RecaptchaVerifier(auth, 'sign-in-button', {
        size: 'invisible',
      });
      
      const confirmation = await signInWithPhoneNumber(auth, phoneNumber, recaptchaVerifier);
      return confirmation.verificationId;
    } catch (error) {
      console.error('Phone sign in error:', error);
      throw error;
    }
  };

  const verifyPhoneCode = async (verificationId: string, code: string): Promise<boolean> => {
    try {
      const credential = PhoneAuthProvider.credential(verificationId, code);
      const currentUser = auth.currentUser;
      
      if (currentUser) {
        await linkWithCredential(currentUser, credential);
        // Update the user profile to mark phone as verified
        await updateUserProfile({ phoneVerified: true });
      }
      
      return true;
    } catch (error) {
      console.error('Phone verification error:', error);
      return false;
    }
  };

  const updateUserProfile = async (profile: Partial<UserProfile>): Promise<boolean> => {
    try {
      if (!auth.currentUser) return false;
      
      await storeUserProfile(auth.currentUser.uid, {
        ...profile,
        updatedAt: new Date()
      });
      
      setUserProfile(prev => prev ? { ...prev, ...profile } : null);
      return true;
    } catch (error) {
      console.error('Profile update error:', error);
      return false;
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
      localStorage.removeItem('authToken');
      setIsAuthenticated(false);
      setUserProfile(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('darkMode', newDarkMode.toString());
  };

  const googleSignIn = async (): Promise<boolean> => {
    try {
      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);
      const token = await result.user.getIdToken();
      localStorage.setItem('authToken', token);
      setIsAuthenticated(true);
      
      // Create/update user profile
      const profile: Omit<UserProfile, 'uid'> = {
        prefix: '',
        firstName: result.user.displayName?.split(' ')[0] || '',
        middleName: '',
        lastName: result.user.displayName?.split(' ').slice(1).join(' ') || '',
        email: result.user.email || '',
        phone: result.user.phoneNumber || '',
        dateOfBirth: '',
        organizationType: '',
        termsAccepted: true,
        phoneVerified: !!result.user.phoneNumber,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      await storeUserProfile(result.user.uid, profile);
      setUserProfile({ ...profile, uid: result.user.uid });
      
      return true;
    } catch (error) {
      console.error('Google Sign-In error:', error);
      return false;
    }
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
