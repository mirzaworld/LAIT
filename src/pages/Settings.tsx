import React, { useState } from 'react';
import { User, Bell, Shield, Database, Zap, Users, Save } from 'lucide-react';

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [notifications, setNotifications] = useState({
    invoiceAlerts: true,
    budgetWarnings: true,
    anomalyDetection: true,
    reportGeneration: false,
    systemUpdates: true,
    emailDigest: true
  });

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'integrations', name: 'Integrations', icon: Database },
    { id: 'ai-settings', name: 'AI Settings', icon: Zap },
    { id: 'team', name: 'Team Management', icon: Users },
  ];

  const handleNotificationChange = (key: string) => {
    setNotifications(prev => ({
      ...prev,
      [key]: !prev[key as keyof typeof prev]
    }));
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  First Name
                </label>
                <input
                  type="text"
                  defaultValue="Sarah"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Last Name
                </label>
                <input
                  type="text"
                  defaultValue="Johnson"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  defaultValue="sarah.johnson@company.com"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Department
                </label>
                <select className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                  <option>Legal Operations</option>
                  <option>Finance</option>
                  <option>Procurement</option>
                  <option>Administration</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Zone
              </label>
              <select className="w-full md:w-1/2 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                <option>Eastern Time (ET)</option>
                <option>Central Time (CT)</option>
                <option>Mountain Time (MT)</option>
                <option>Pacific Time (PT)</option>
              </select>
            </div>
          </div>
        );

      case 'notifications':
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              {Object.entries(notifications).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between py-3 border-b border-gray-200 last:border-b-0">
                  <div>
                    <h4 className="font-medium text-gray-900">
                      {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                    </h4>
                    <p className="text-sm text-gray-500">
                      {key === 'invoiceAlerts' && 'Get notified when new invoices are received'}
                      {key === 'budgetWarnings' && 'Receive alerts when budgets exceed thresholds'}
                      {key === 'anomalyDetection' && 'AI-powered anomaly detection notifications'}
                      {key === 'reportGeneration' && 'Updates on report generation status'}
                      {key === 'systemUpdates' && 'Important system updates and maintenance'}
                      {key === 'emailDigest' && 'Weekly summary of legal spend activity'}
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={() => handleNotificationChange(key)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>
        );

      case 'security':
        return (
          <div className="space-y-6">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex">
                <Shield className="w-5 h-5 text-yellow-400 mr-3 mt-0.5" />
                <div>
                  <h4 className="font-medium text-yellow-800">Security Status: Good</h4>
                  <p className="text-sm text-yellow-700 mt-1">Last security scan completed 2 days ago</p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Password Settings</h4>
                <button className="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50">
                  Change Password
                </button>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Two-Factor Authentication</h4>
                <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">SMS Authentication</p>
                    <p className="text-sm text-gray-500">+1 (555) 123-4567</p>
                  </div>
                  <span className="px-2 py-1 bg-success-100 text-success-700 text-xs font-medium rounded-full">
                    Enabled
                  </span>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-3">Active Sessions</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">Chrome on MacOS</p>
                      <p className="text-sm text-gray-500">New York, NY - Current session</p>
                    </div>
                    <span className="text-success-600 text-sm font-medium">Active</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'integrations':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">Workday</h4>
                  <span className="px-2 py-1 bg-success-100 text-success-700 text-xs font-medium rounded-full">
                    Connected
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">Financial management and budgeting</p>
                <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                  Configure
                </button>
              </div>

              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">Salesforce</h4>
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">
                    Not Connected
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">CRM and matter management</p>
                <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                  Connect
                </button>
              </div>

              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">NetSuite</h4>
                  <span className="px-2 py-1 bg-success-100 text-success-700 text-xs font-medium rounded-full">
                    Connected
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">ERP and financial reporting</p>
                <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                  Configure
                </button>
              </div>

              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">Clio</h4>
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">
                    Not Connected
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">Legal practice management</p>
                <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                  Connect
                </button>
              </div>
            </div>
          </div>
        );

      case 'ai-settings':
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex">
                <Zap className="w-5 h-5 text-blue-400 mr-3 mt-0.5" />
                <div>
                  <h4 className="font-medium text-blue-800">AI Engine Status: Active</h4>
                  <p className="text-sm text-blue-700 mt-1">Processing 1,247 invoices with 94.7% accuracy</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Anomaly Detection Sensitivity</h4>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">Low</span>
                  <input type="range" min="1" max="100" defaultValue="75" className="flex-1" />
                  <span className="text-sm text-gray-600">High</span>
                </div>
                <p className="text-sm text-gray-500 mt-2">Currently set to 75% - Balance between detection and false positives</p>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-3">Auto-Approval Thresholds</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Maximum Amount</label>
                    <input
                      type="number"
                      defaultValue="5000"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Confidence Score</label>
                    <input
                      type="number"
                      defaultValue="95"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-3">Learning Preferences</h4>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input type="checkbox" defaultChecked className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded" />
                    <span className="ml-3 text-sm text-gray-700">Learn from user approvals</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" defaultChecked className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded" />
                    <span className="ml-3 text-sm text-gray-700">Adapt to vendor patterns</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded" />
                    <span className="ml-3 text-sm text-gray-700">Share insights with other departments</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        );

      case 'team':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-gray-900">Team Members</h4>
              <button className="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700">
                Invite Member
              </button>
            </div>

            <div className="space-y-3">
              {[
                { name: 'Sarah Johnson', email: 'sarah.johnson@company.com', role: 'Admin', status: 'Active' },
                { name: 'Michael Chen', email: 'michael.chen@company.com', role: 'Manager', status: 'Active' },
                { name: 'Emily Rodriguez', email: 'emily.rodriguez@company.com', role: 'Analyst', status: 'Active' },
                { name: 'David Kim', email: 'david.kim@company.com', role: 'Viewer', status: 'Pending' },
              ].map((member, index) => (
                <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-600">
                        {member.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{member.name}</p>
                      <p className="text-sm text-gray-500">{member.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-600">{member.role}</span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      member.status === 'Active' 
                        ? 'bg-success-100 text-success-700' 
                        : 'bg-warning-100 text-warning-700'
                    }`}>
                      {member.status}
                    </span>
                    <button className="text-sm text-primary-600 hover:text-primary-700">
                      Edit
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your account settings and preferences
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Navigation */}
        <div className="lg:col-span-1">
          <nav className="space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 text-sm font-medium rounded-lg transition-colors duration-200 ${
                    activeTab === tab.id
                      ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">
                {tabs.find(tab => tab.id === activeTab)?.name}
              </h3>
              <button className="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200">
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </button>
            </div>
            
            {renderTabContent()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;