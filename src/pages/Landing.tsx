import React from 'react';
import { Link } from 'react-router-dom';
import { DollarSign, Shield, BarChart2, FileText, TrendingUp, CheckCircle } from 'lucide-react';

const Landing: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation */}
      <nav className="bg-white shadow-sm py-4 px-6">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-lg">
              <DollarSign className="w-6 h-6 text-white" />
            </div>
            <span className="font-bold text-xl text-gray-900">LAIT</span>
          </div>
          <div className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-gray-600 hover:text-primary-600 transition-colors">Features</a>
            <a href="#how-it-works" className="text-gray-600 hover:text-primary-600 transition-colors">How It Works</a>
            <a href="#pricing" className="text-gray-600 hover:text-primary-600 transition-colors">Pricing</a>
            <a href="#testimonials" className="text-gray-600 hover:text-primary-600 transition-colors">Testimonials</a>
          </div>
          <div className="flex items-center space-x-4">
            <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">Login</Link>
            <Link to="/signup" className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-50 to-blue-50 py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl font-bold text-gray-900 leading-tight">
                AI-Powered Legal Invoice Analysis
              </h1>
              <p className="mt-6 text-xl text-gray-600">
                Streamline your legal spend management. Automatically extract data from invoices, 
                gain insights, and optimize your legal budget with our AI-powered platform.
              </p>
              <div className="mt-10 flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
                <Link 
                  to="/signup" 
                  className="bg-primary-600 text-white text-center px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors font-medium"
                >
                  Start Free Trial
                </Link>
                <a 
                  href="#demo" 
                  className="border border-gray-300 bg-white text-gray-700 text-center px-6 py-3 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  Watch Demo
                </a>
              </div>
            </div>
            <div className="hidden md:block">
              <img 
                src="/dashboard-preview.png" 
                alt="Dashboard Preview" 
                className="rounded-lg shadow-xl"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.src = "https://via.placeholder.com/600x400?text=Dashboard+Preview";
                }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900">Key Features</h2>
            <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
              Our platform offers powerful tools to help legal departments manage their spending effectively.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="p-3 bg-primary-100 rounded-lg inline-block mb-4">
                <FileText className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Invoice OCR</h3>
              <p className="text-gray-600">
                Automatically extract key data from legal invoices using our advanced OCR technology.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="p-3 bg-primary-100 rounded-lg inline-block mb-4">
                <BarChart2 className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Spend Analytics</h3>
              <p className="text-gray-600">
                Gain insights into your legal spending patterns with detailed analytics and visualizations.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="p-3 bg-primary-100 rounded-lg inline-block mb-4">
                <TrendingUp className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Forecasting</h3>
              <p className="text-gray-600">
                Predict future legal expenses using AI-powered forecasting algorithms.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="p-3 bg-primary-100 rounded-lg inline-block mb-4">
                <Shield className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Compliance Checks</h3>
              <p className="text-gray-600">
                Automatically validate invoices against billing guidelines and flag potential issues.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="p-3 bg-primary-100 rounded-lg inline-block mb-4">
                <CheckCircle className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Approval Workflow</h3>
              <p className="text-gray-600">
                Streamline your invoice approval process with customizable workflow automation.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="p-3 bg-primary-100 rounded-lg inline-block mb-4">
                <FileText className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Vendor Management</h3>
              <p className="text-gray-600">
                Track vendor performance and spending to optimize your legal service provider relationships.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900">How It Works</h2>
            <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
              Our platform simplifies legal invoice management in a few easy steps.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-6">
                1
              </div>
              <h3 className="text-xl font-semibold mb-4">Upload Invoices</h3>
              <p className="text-gray-600">
                Simply upload your legal invoices through our secure platform, or connect with your existing systems.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-6">
                2
              </div>
              <h3 className="text-xl font-semibold mb-4">AI Processing</h3>
              <p className="text-gray-600">
                Our AI engine automatically extracts and categorizes all invoice data, flagging anomalies.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-6">
                3
              </div>
              <h3 className="text-xl font-semibold mb-4">Gain Insights</h3>
              <p className="text-gray-600">
                Access detailed analytics dashboard to visualize spending patterns and identify cost-saving opportunities.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900">Simple, Transparent Pricing</h2>
            <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
              Choose the plan that's right for your organization.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Starter Plan */}
            <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
              <h3 className="text-xl font-semibold mb-2">Starter</h3>
              <p className="text-gray-500 mb-6">For small legal departments</p>
              <div className="mb-6">
                <span className="text-4xl font-bold">$199</span>
                <span className="text-gray-500">/month</span>
              </div>
              <ul className="mb-8 space-y-3">
                <li className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  <span>Up to 100 invoices/month</span>
                </li>
                <li className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  <span>Basic analytics</span>
                </li>
                <li className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  <span>Email support</span>
                </li>
              </ul>
              <Link to="/signup" className="block w-full bg-white border border-primary-600 text-primary-600 text-center px-6 py-3 rounded-lg hover:bg-primary-50 transition-colors font-medium">
                Start Free Trial
              </Link>
            </div>

            {/* Business Plan */}
            <div className="bg-primary-600 p-8 rounded-lg shadow-md transform md:scale-105">
              <h3 className="text-xl font-semibold mb-2 text-white">Business</h3>
              <p className="text-primary-100 mb-6">For mid-size legal teams</p>
              <div className="mb-6">
                <span className="text-4xl font-bold text-white">$499</span>
                <span className="text-primary-100">/month</span>
              </div>
              <ul className="mb-8 space-y-3">
                <li className="flex items-center text-white">
                  <CheckCircle className="w-5 h-5 text-primary-100 mr-2" />
                  <span>Up to 500 invoices/month</span>
                </li>
                <li className="flex items-center text-white">
                  <CheckCircle className="w-5 h-5 text-primary-100 mr-2" />
                  <span>Advanced analytics</span>
                </li>
                <li className="flex items-center text-white">
                  <CheckCircle className="w-5 h-5 text-primary-100 mr-2" />
                  <span>Priority support</span>
                </li>
                <li className="flex items-center text-white">
                  <CheckCircle className="w-5 h-5 text-primary-100 mr-2" />
                  <span>API access</span>
                </li>
              </ul>
              <Link to="/signup" className="block w-full bg-white text-primary-600 text-center px-6 py-3 rounded-lg hover:bg-primary-50 transition-colors font-medium">
                Start Free Trial
              </Link>
            </div>

            {/* Enterprise Plan */}
            <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
              <h3 className="text-xl font-semibold mb-2">Enterprise</h3>
              <p className="text-gray-500 mb-6">For large organizations</p>
              <div className="mb-6">
                <span className="text-4xl font-bold">Custom</span>
              </div>
              <ul className="mb-8 space-y-3">
                <li className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  <span>Unlimited invoices</span>
                </li>
                <li className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  <span>Custom integrations</span>
                </li>
                <li className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  <span>Dedicated account manager</span>
                </li>
                <li className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  <span>Custom reporting</span>
                </li>
              </ul>
              <Link to="/contact" className="block w-full bg-white border border-gray-300 text-gray-700 text-center px-6 py-3 rounded-lg hover:bg-gray-50 transition-colors font-medium">
                Contact Sales
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900">What Our Customers Say</h2>
            <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
              Trusted by legal departments across industries.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center mb-4">
                <div className="text-yellow-400 flex">
                  {[...Array(5)].map((_, i) => (
                    <svg key={i} className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                      <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                    </svg>
                  ))}
                </div>
              </div>
              <p className="text-gray-600 mb-6">
                "LAIT has transformed how we manage our legal invoices. The AI extraction is incredibly accurate, and the insights have helped us reduce our outside counsel spending by 15%."
              </p>
              <div>
                <p className="font-medium">Sarah Johnson</p>
                <p className="text-gray-500 text-sm">General Counsel, Tech Industries Inc.</p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center mb-4">
                <div className="text-yellow-400 flex">
                  {[...Array(5)].map((_, i) => (
                    <svg key={i} className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                      <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                    </svg>
                  ))}
                </div>
              </div>
              <p className="text-gray-600 mb-6">
                "The platform's compliance checks have caught billing guideline violations that we would have missed. It pays for itself in savings alone."
              </p>
              <div>
                <p className="font-medium">Michael Chen</p>
                <p className="text-gray-500 text-sm">Legal Operations Manager, Global Finance Corp</p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center mb-4">
                <div className="text-yellow-400 flex">
                  {[...Array(5)].map((_, i) => (
                    <svg key={i} className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                      <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                    </svg>
                  ))}
                </div>
              </div>
              <p className="text-gray-600 mb-6">
                "Implementation was smooth, and our team adopted it quickly. The analytics dashboard has become an essential tool for our monthly budget reviews."
              </p>
              <div>
                <p className="font-medium">Rebecca Torres</p>
                <p className="text-gray-500 text-sm">Associate GC, Healthcare Systems Ltd</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-primary-600">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">Ready to transform your legal invoice management?</h2>
          <p className="text-xl text-primary-100 mb-8 max-w-3xl mx-auto">
            Join hundreds of legal departments using LAIT to streamline their invoice processing and gain valuable insights.
          </p>
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <Link 
              to="/signup" 
              className="bg-white text-primary-700 px-8 py-3 rounded-lg hover:bg-primary-50 transition-colors font-medium"
            >
              Start Your Free Trial
            </Link>
            <Link 
              to="/contact" 
              className="bg-transparent border border-white text-white px-8 py-3 rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              Schedule a Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-white font-semibold mb-4">Product</h3>
              <ul className="space-y-2">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Integrations</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Updates</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Company</h3>
              <ul className="space-y-2">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#contact" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Resources</h3>
              <ul className="space-y-2">
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Community</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Legal</h3>
              <ul className="space-y-2">
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2">
              <div className="flex items-center justify-center w-8 h-8 bg-primary-600 rounded-lg">
                <DollarSign className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-white">LAIT</span>
            </div>
            <p className="mt-4 md:mt-0">© {new Date().getFullYear()} LAIT. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
