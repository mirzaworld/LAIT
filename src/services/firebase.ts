import { initializeApp } from 'firebase/app';
import { getAuth, RecaptchaVerifier } from 'firebase/auth';
import { getFirestore, doc, setDoc, getDoc } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyDgR3LH961uM18WD5eNpzzA9f7vJa3iwEA",
  authDomain: "lait-6e921.firebaseapp.com",
  projectId: "lait-6e921",
  storageBucket: "lait-6e921.firebasestorage.app",
  messagingSenderId: "435544872587",
  appId: "1:435544872587:web:d6970332bf4d74ae7a268e",
  measurementId: "G-NC5KP4PTDT"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// Initialize Firebase Auth and get a reference to the service
auth.useDeviceLanguage();

// Initialize reCAPTCHA verifier
let recaptchaVerifier: RecaptchaVerifier | null = null;

// Log the initialization status
console.log('Firebase initialized successfully');
console.log('Current auth state:', auth.currentUser);

// Listen for auth state changes
auth.onAuthStateChanged((user) => {
  console.log('Auth state changed:', user ? 'User is signed in' : 'User is signed out');
  if (user) {
    console.log('User details:', {
      email: user.email,
      emailVerified: user.emailVerified,
      uid: user.uid
    });
  }
});

// Store additional user data in Firestore
export const storeUserProfile = async (userId: string, userData: any) => {
  try {
    const userRef = doc(db, 'users', userId);
    await setDoc(userRef, {
      ...userData,
      createdAt: new Date(),
      updatedAt: new Date()
    }, { merge: true });
    return true;
  } catch (error) {
    console.error('Error storing user profile:', error);
    return false;
  }
};

// Get user profile from Firestore
export const getUserProfile = async (userId: string) => {
  try {
    const userRef = doc(db, 'users', userId);
    const userDoc = await getDoc(userRef);
    return userDoc.exists() ? userDoc.data() : null;
  } catch (error) {
    console.error('Error getting user profile:', error);
    return null;
  }
};

export { auth, db };
