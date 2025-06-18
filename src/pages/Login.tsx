import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { DollarSign, Lock, Mail, Loader2 } from 'lucide-react';
import { useApp } from '../context/AppContext';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const navigate = useNavigate();
  const { login, isAuthenticated } = useApp();
  
  useEffect(() => {
    console.log('Login page mounted');
    console.log('Is authenticated:', isAuthenticated);
  }, [isAuthenticated]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Login attempt with email:', email);
    setError(null);
    setIsLoading(true);
    
    try {
      const success = await login(email, password);
      console.log('Login result:', success);
      if (success) {
        console.log('Navigation to /');
        navigate('/');
      } else {
        setError('Invalid credentials. Please try again.');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('An error occurred while logging in. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center">
            <div className="flex items-center justify-center w-12 h-12 bg-primary-600 rounded-lg">
              <DollarSign className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="mt-4 text-2xl font-bold text-gray-900">LAIT - Legal AI Spend Optimizer</h1>
          <p className="mt-2 text-gray-500">Sign in to your account</p>
        </div>
        
        <div className="bg-white p-8 shadow-lg rounded-xl border border-gray-200">
          {error && (
            <div className="mb-4 p-3 bg-danger-50 text-danger-700 rounded-lg text-sm">
              {error}
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="pl-10 block w-full rounded-lg border border-gray-300 py-2 px-3 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="you@example.com"
                />
              </div>
            </div>
            
            <div className="mb-6">
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="pl-10 block w-full rounded-lg border border-gray-300 py-2 px-3 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="••••••••"
                />
              </div>
            </div>
            
            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-lg bg-primary-600 py-2 px-4 text-white font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition duration-150 disabled:opacity-50"
            >
              {isLoading ? (
                <div className="flex justify-center items-center">
                  <Loader2 className="animate-spin h-5 w-5 mr-2" />
                  Signing in...
                </div>
              ) : (
                'Sign In'
              )}
            </button>
          </form>
          
          <div className="mt-6 text-center text-sm">
            <p className="text-gray-500">
              Don't have an account? <Link to="/signup" className="text-primary-600 hover:underline">Sign up</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
