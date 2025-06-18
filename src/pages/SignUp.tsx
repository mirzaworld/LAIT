import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { DollarSign, Mail, Lock, Phone, User, Calendar, Building, Loader2, AlertTriangle } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { auth } from '../services/firebase';

const organizationTypes = [
  { value: 'company', label: 'Company' },
  { value: 'corporation', label: 'Corporation' },
  { value: 'education', label: 'Educational Institution' },
  { value: 'student', label: 'Student' },
  { value: 'other', label: 'Other' }
];

const prefixes = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.'];

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

const SignUp: React.FC = () => {
  const [formData, setFormData] = useState<SignUpForm>({
    prefix: '',
    firstName: '',
    middleName: '',
    lastName: '',
    email: '',
    password: '',
    phone: '',
    dateOfBirth: '',
    organizationType: '',
    termsAccepted: false
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'signup' | 'verify'>('signup');
  const [verificationId, setVerificationId] = useState<string>('');
  const [verificationCode, setVerificationCode] = useState<string>('');
  const [verificationError, setVerificationError] = useState<string | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  
  const navigate = useNavigate();
  const { signup, isAuthenticated, googleSignIn, phoneSignIn, verifyPhoneCode } = useApp();

  useEffect(() => {
    console.log('SignUp page mounted');
    if (isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.termsAccepted) {
      setError('Please accept the terms and conditions');
      return;
    }
    
    setError(null);
    setIsLoading(true);

    try {
      if (step === 'signup') {
        const success = await signup(formData);
        if (success) {
          // Start phone verification
          try {
            const verificationId = await phoneSignIn(formData.phone);
            setVerificationId(verificationId);
            setStep('verify');
          } catch (err: any) {
            setError('Failed to send verification code. Please try again.');
          }
        } else {
          setError('Failed to create account. Please try again.');
        }
      }
    } catch (err: any) {
      console.error('Signup error:', err);
      setError(err?.message || 'An error occurred while signing up. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerificationSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!verificationCode) {
      setVerificationError('Please enter the verification code');
      return;
    }

    setVerificationError(null);
    setIsVerifying(true);

    try {
      const success = await verifyPhoneCode(verificationId, verificationCode);
      if (success) {
        console.log('Phone verified successfully');
        navigate('/', { replace: true });
      } else {
        setVerificationError('Invalid verification code. Please try again.');
      }
    } catch (err: any) {
      console.error('Verification error:', err);
      setVerificationError(err?.message || 'Failed to verify code. Please try again.');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      const success = await googleSignIn();
      if (success) {
        navigate('/');
      } else {
        setError('Failed to sign in with Google. Please try again.');
      }
    } catch (err) {
      setError('An error occurred while signing in with Google.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gray-50 px-4 py-8">
      <div className="w-full max-w-2xl">
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center">
            <div className="flex items-center justify-center w-12 h-12 bg-primary-600 rounded-lg">
              <DollarSign className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="mt-4 text-2xl font-bold text-gray-900">
            {step === 'signup' ? 'Create an Account' : 'Verify Phone Number'}
          </h1>
          <p className="mt-2 text-gray-500">
            {step === 'signup' 
              ? 'Sign up to access Legal AI Spend Optimizer'
              : 'Enter the verification code sent to your phone'
            }
          </p>
        </div>

        <div className="bg-white p-8 shadow-lg rounded-xl border border-gray-200">
          {error && (
            <div className="mb-4 p-3 bg-danger-50 text-danger-700 rounded-lg text-sm flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2 flex-shrink-0" />
              {error}
            </div>
          )}

          {step === 'signup' ? (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Prefix
                  </label>
                  <select
                    name="prefix"
                    value={formData.prefix}
                    onChange={handleInputChange}
                    className="block w-full rounded-lg border border-gray-300 py-2 px-3"
                    required
                  >
                    <option value="">Select prefix</option>
                    {prefixes.map(prefix => (
                      <option key={prefix} value={prefix}>{prefix}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    First Name
                  </label>
                  <input
                    name="firstName"
                    type="text"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    required
                    className="block w-full rounded-lg border border-gray-300 py-2 px-3"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Middle Name
                  </label>
                  <input
                    name="middleName"
                    type="text"
                    value={formData.middleName}
                    onChange={handleInputChange}
                    className="block w-full rounded-lg border border-gray-300 py-2 px-3"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Name
                  </label>
                  <input
                    name="lastName"
                    type="text"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    required
                    className="block w-full rounded-lg border border-gray-300 py-2 px-3"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <input
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      className="block w-full rounded-lg border border-gray-300 py-2 pl-10 pr-3"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <input
                      name="password"
                      type="password"
                      value={formData.password}
                      onChange={handleInputChange}
                      required
                      minLength={8}
                      className="block w-full rounded-lg border border-gray-300 py-2 pl-10 pr-3"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <input
                      name="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={handleInputChange}
                      required
                      placeholder="+1 (555) 555-5555"
                      className="block w-full rounded-lg border border-gray-300 py-2 pl-10 pr-3"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date of Birth
                  </label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <input
                      name="dateOfBirth"
                      type="date"
                      value={formData.dateOfBirth}
                      onChange={handleInputChange}
                      required
                      className="block w-full rounded-lg border border-gray-300 py-2 pl-10 pr-3"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Organization Type
                </label>
                <div className="relative">
                  <Building className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                  <select
                    name="organizationType"
                    value={formData.organizationType}
                    onChange={handleInputChange}
                    required
                    className="block w-full rounded-lg border border-gray-300 py-2 pl-10 pr-3"
                  >
                    <option value="">Select organization type</option>
                    {organizationTypes.map(org => (
                      <option key={org.value} value={org.value}>{org.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex items-center">
                <input
                  name="termsAccepted"
                  type="checkbox"
                  checked={formData.termsAccepted}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  I accept the <Link to="/terms" className="text-primary-600 hover:text-primary-500">terms and conditions</Link>
                </label>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    'Create Account'
                  )}
                </button>
              </div>

              <div className="mt-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">Or continue with</span>
                  </div>
                </div>

                <div className="mt-6">
                  <button
                    type="button"
                    onClick={handleGoogleSignIn}
                    className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                      <path
                        fill="#4285F4"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="#34A853"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="#FBBC05"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="#EA4335"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                      <path fill="none" d="M1 1h22v22H1z" />
                    </svg>
                    Sign up with Google
                  </button>
                </div>
              </div>

              <div className="text-center mt-6">
                <p className="text-sm text-gray-600">
                  Already have an account?{' '}
                  <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
                    Sign in
                  </Link>
                </p>
              </div>
            </form>
          ) : (
            <form onSubmit={handleVerificationSubmit} className="space-y-6">
              {verificationError && (
                <div className="mb-4 p-3 bg-danger-50 text-danger-700 rounded-lg text-sm flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2 flex-shrink-0" />
                  {verificationError}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Verification Code
                </label>
                <input
                  type="text"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  placeholder="Enter 6-digit code"
                  required
                  className="block w-full rounded-lg border border-gray-300 py-2 px-3"
                />
              </div>

              <div>
                <button
                  type="submit"
                  disabled={isVerifying}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  {isVerifying ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    'Verify Code'
                  )}
                </button>
              </div>

              <div className="text-center mt-4">
                <p className="text-sm text-gray-500">
                  Didn't receive the code?{' '}
                  <button
                    type="button"
                    onClick={() => setStep('signup')}
                    className="text-primary-600 hover:text-primary-500"
                  >
                    Try again
                  </button>
                </p>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default SignUp;
