import React, { useState } from 'react';
import { Building2, TrendingUp, TrendingDown, Loader2, ExternalLink } from 'lucide-react';
import { useVendors } from '../hooks/useApi';
import { useNavigate } from 'react-router-dom';

const TopVendors: React.FC = () => {
  const navigate = useNavigate();
  const { vendors, loading, error } = useVendors();
  const [selectedVendor, setSelectedVendor] = useState<string | null>(null);
  
  const handleViewVendor = (id: string) => {
    setSelectedVendor(id);
    navigate(`/analytics/vendors/${id}`);
  };

  // Calculate percent change based on performance score (simulating change)
  const getChangePercent = (score: number) => {
    // Use performance score to simulate a percent change value
    // Higher score = better performance = positive change
    return score > 80 ? (score - 80) : (score - 80);
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Top Vendors</h3>
          <p className="text-sm text-gray-500">Highest spending law firms this quarter</p>
        </div>
        <button 
          onClick={() => navigate('/analytics')}
          className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center"
        >
          View All <ExternalLink className="ml-1 w-3 h-3" />
        </button>
      </div>
      
      {loading ? (
        <div className="flex items-center justify-center p-8">
          <Loader2 className="w-6 h-6 text-primary-500 animate-spin" />
          <span className="ml-2 text-sm text-gray-500">Loading vendors...</span>
        </div>
      ) : error ? (
        <div className="p-4 text-center text-danger-600 bg-danger-50 rounded-lg">
          <p>Error loading vendors. Please try again.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {vendors.slice(0, 5).map((vendor, index) => {
            const changePercent = getChangePercent(vendor.performance_score);
            
            return (
              <div 
                key={vendor.id}
                className="flex items-center justify-between p-4 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors duration-200 animate-slide-up cursor-pointer"
                style={{ animationDelay: `${index * 50}ms` }}
                onClick={() => handleViewVendor(vendor.id)}
              >
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                      <Building2 className="w-5 h-5 text-primary-600" />
                    </div>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {vendor.name}
                    </p>
                    <div className="flex items-center space-x-4 mt-1">
                      <p className="text-xs text-gray-500">{vendor.category}</p>
                      <p className="text-xs text-gray-500">{vendor.matter_count} matters</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm font-semibold text-gray-900">
                      ${vendor.spend.toLocaleString()}
                    </p>
                    <div className={`flex items-center space-x-1 text-xs ${
                      changePercent >= 0 ? 'text-success-600' : 'text-danger-600'
                    }`}>
                      {changePercent >= 0 ? (
                        <TrendingUp className="w-3 h-3" />
                      ) : (
                        <TrendingDown className="w-3 h-3" />
                      )}
                      <span>{Math.abs(changePercent).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default TopVendors;