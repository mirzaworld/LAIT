import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Bell,
  Moon,
  Sun,
  Menu,
  X,
  Home,
  PieChart,
  FileText,
  Settings,
  Upload,
  AlertTriangle,
  CheckCircle,
  LogOut,
  Scale,
  Brain
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { useAuth } from '../context/AuthContext';
import { useNotificationContext } from '../context/NotificationContext';
import { NotificationItem } from './NotificationItem';
import ApiHealthIndicator from './ApiHealthIndicator';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const location = useLocation();
  const navigate = useNavigate();
  const { darkMode, toggleDarkMode, logout, userProfile } = useApp();
  const { user, logout: authLogout } = useAuth();
  const { notifications, hasUnread, markAllRead, clearNotifications } = useNotificationContext();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Upload Invoice', href: '/invoices/upload', icon: Upload },
    { name: 'Legal Intelligence', href: '/legal-intelligence', icon: Scale },
    { name: 'Analytics', href: '/analytics', icon: PieChart },
    { name: 'Reports', href: '/reports', icon: FileText },
    { name: 'Vendors', href: '/vendors', icon: Settings },
    { name: 'Settings', href: '/settings', icon: Settings }
  ];

  const isActive = (href: string) => {
    return location.pathname === href;
  };

  const handleNotificationAction = (action: string) => {
    switch (action) {
      case 'view':
        // Navigate to invoice details
        break;
      case 'approve':
        // Handle invoice approval
        break;
      case 'reject':
        // Handle invoice rejection
        break;
      case 'viewVendor':
        // Navigate to vendor details
        break;
    }
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className={`min-h-screen ${
        darkMode ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-900'
      }`}>
        {/* Sidebar */}
        <aside
          className={`fixed top-0 left-0 z-40 w-64 h-screen transition-transform ${
            isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
          } ${darkMode ? 'bg-gray-800' : 'bg-white'} shadow-lg`}
        >
          <div className="h-full px-3 py-4 overflow-y-auto">
            <div className="flex items-center justify-between mb-5">
              <span className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                LAIT
              </span>
              <button
                onClick={() => setIsSidebarOpen(false)}
                className={`lg:hidden ${darkMode ? 'text-white' : 'text-gray-500'}`}
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            {/* Navigation Links */}
            <nav className="space-y-2">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                    isActive(item.href)
                      ? `${darkMode ? 'bg-gray-700 text-white' : 'bg-gray-200 text-gray-900'}`
                      : `${darkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-600 hover:bg-gray-100'}`
                  }`}
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  <span>{item.name}</span>
                </Link>
              ))}
              <button
                onClick={handleLogout}
                className={`w-full flex items-center px-4 py-2 rounded-lg transition-colors ${
                  darkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <LogOut className="w-5 h-5 mr-3" />
                <span>Logout</span>
              </button>
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <div className={`lg:ml-64 min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-100'}`}>
          {/* Header */}
          <header className={`fixed top-0 right-0 z-30 w-full h-16 ${
            darkMode ? 'bg-gray-800 border-b border-gray-700' : 'bg-white border-b'
          } shadow-sm lg:ml-64 px-4`}>
            <div className="h-full flex items-center justify-between max-w-screen-2xl mx-auto">
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="lg:hidden"
              >
                <Menu className={`w-6 h-6 ${darkMode ? 'text-white' : 'text-gray-500'}`} />
              </button>

              <div className="flex items-center space-x-4">
                {/* Search */}
                <form onSubmit={handleSearch} className="hidden md:flex">
                  <input
                    type="search"
                    placeholder="Search..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className={`px-4 py-2 rounded-lg ${
                      darkMode ? 'bg-gray-700 text-white' : 'bg-gray-100'
                    } focus:outline-none focus:ring-2 focus:ring-primary-500`}
                  />
                </form>

                {/* Dark Mode Toggle */}
                <button
                  onClick={toggleDarkMode}
                  className={`p-2 rounded-lg ${
                    darkMode ? 'bg-gray-700 text-white' : 'hover:bg-gray-100'
                  }`}
                >
                  {darkMode ? (
                    <Sun className="w-5 h-5" />
                  ) : (
                    <Moon className="w-5 h-5" />
                  )}
                </button>

                {/* API Health Status */}
                <ApiHealthIndicator />

                {/* Notifications */}
                <div className="relative">
                  <button
                    onClick={() => setShowNotifications(!showNotifications)}
                    className={`relative p-2 rounded-lg ${
                      darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                    }`}
                  >
                    <Bell className={`w-6 h-6 ${darkMode ? 'text-white' : 'text-gray-500'}`} />
                    {hasUnread && (
                      <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full"></span>
                    )}
                  </button>

                  {showNotifications && (
                    <div className={`absolute right-0 mt-2 w-96 rounded-lg shadow-lg ${
                      darkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
                    } ring-1 ring-black ring-opacity-5`}>
                      <div className="p-4">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className={`text-lg font-medium ${
                            darkMode ? 'text-white' : 'text-gray-900'
                          }`}>
                            Notifications
                          </h3>
                          <div className="space-x-2">
                            <button
                              onClick={markAllRead}
                              className="text-xs text-blue-500 hover:text-blue-600"
                            >
                              Mark all read
                            </button>
                            <button
                              onClick={clearNotifications}
                              className="text-xs text-gray-500 hover:text-gray-600"
                            >
                              Clear all
                            </button>
                          </div>
                        </div>

                        <div className="space-y-4 max-h-96 overflow-y-auto">
                          {notifications.length === 0 ? (
                            <p className={`text-sm ${
                              darkMode ? 'text-gray-400' : 'text-gray-500'
                            }`}>
                              No notifications
                            </p>
                          ) : (
                            notifications.map((notification) => (
                              <NotificationItem
                                key={`${notification.type}-${notification.timestamp}`}
                                notification={notification}
                                onAction={handleNotificationAction}
                              />
                            ))
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* User Profile */}
                {userProfile && (
                  <div className={`hidden md:block text-right ${
                    darkMode ? 'text-white' : 'text-gray-900'
                  }`}>
                    <p className="text-sm font-medium">
                      {`${userProfile.prefix} ${userProfile.firstName} ${userProfile.lastName}`}
                    </p>
                    <p className="text-xs text-gray-500">
                      {userProfile.organizationType}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="pt-16 min-h-screen">
            <div className="max-w-screen-2xl mx-auto p-4">
              {children}
            </div>
          </main>
        </div>
      </div>

      {/* Toast Container */}
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="colored"
      />
    </div>
  );
};

export default Layout;