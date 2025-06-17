import React from 'react';
import { Building2, TrendingUp, TrendingDown } from 'lucide-react';

const TopVendors: React.FC = () => {
  const vendors = [
    {
      name: 'Morrison & Foerster LLP',
      spend: 847392,
      change: 12.5,
      matters: 23,
      category: 'IP Litigation'
    },
    {
      name: 'Baker McKenzie',
      spend: 623450,
      change: -8.2,
      matters: 18,
      category: 'Corporate'
    },
    {
      name: 'Latham & Watkins',
      spend: 567800,
      change: 15.3,
      matters: 31,
      category: 'M&A'
    },
    {
      name: 'Skadden Arps',
      spend: 445600,
      change: 3.7,
      matters: 14,
      category: 'Securities'
    },
    {
      name: 'White & Case',
      spend: 398200,
      change: -2.1,
      matters: 19,
      category: 'International'
    }
  ];

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Top Vendors</h3>
          <p className="text-sm text-gray-500">Highest spending law firms this quarter</p>
        </div>
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          View All
        </button>
      </div>
      
      <div className="space-y-4">
        {vendors.map((vendor, index) => (
          <div 
            key={vendor.name}
            className="flex items-center justify-between p-4 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors duration-200 animate-slide-up"
            style={{ animationDelay: `${index * 50}ms` }}
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
                  <p className="text-xs text-gray-500">{vendor.matters} matters</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-semibold text-gray-900">
                  ${vendor.spend.toLocaleString()}
                </p>
                <div className={`flex items-center space-x-1 text-xs ${
                  vendor.change >= 0 ? 'text-success-600' : 'text-danger-600'
                }`}>
                  {vendor.change >= 0 ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                  <span>{Math.abs(vendor.change)}%</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopVendors;