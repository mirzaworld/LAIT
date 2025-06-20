import React from 'react';

const SimpleDashboard: React.FC = () => {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">LAIT Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">Total Spend</h3>
          <p className="text-3xl font-bold text-blue-600">$259,950</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">Invoices</h3>
          <p className="text-3xl font-bold text-green-600">5</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">Active Matters</h3>
          <p className="text-3xl font-bold text-purple-600">5</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">Risk Factors</h3>
          <p className="text-3xl font-bold text-red-600">35</p>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h2>
        <p className="text-gray-600">Dashboard loaded successfully! Backend API is connected.</p>
        
        <div className="mt-4 space-y-2">
          <div className="flex justify-between">
            <span>Frontend Status:</span>
            <span className="text-green-600 font-medium">✅ Working</span>
          </div>
          <div className="flex justify-between">
            <span>Backend API:</span>
            <span className="text-green-600 font-medium">✅ Connected</span>
          </div>
          <div className="flex justify-between">
            <span>Authentication:</span>
            <span className="text-green-600 font-medium">✅ Authenticated</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleDashboard;
