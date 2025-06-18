import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Info, X } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string;
  change: string;
  changeType: 'increase' | 'decrease';
  icon: LucideIcon;
  period: string;
  index: number;
  detailsInfo?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  changeType,
  icon: Icon,
  period,
  index,
  detailsInfo = "Click for detailed breakdown and historical trends."
}) => {
  const isPositive = changeType === 'increase';
  const TrendIcon = isPositive ? TrendingUp : TrendingDown;
  const [showDetails, setShowDetails] = useState(false);
  
  const toggleDetails = () => {
    setShowDetails(!showDetails);
  };

  return (
    <div 
      className="relative bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all duration-300 animate-slide-up cursor-pointer"
      style={{ animationDelay: `${index * 100}ms` }}
      onClick={toggleDetails}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${
            isPositive ? 'bg-success-100' : 'bg-primary-100'
          }`}>
            <Icon className={`w-5 h-5 ${
              isPositive ? 'text-success-600' : 'text-primary-600'
            }`} />
          </div>
        </div>
        <div className={`flex items-center space-x-1 text-sm font-medium ${
          isPositive ? 'text-success-600' : 'text-danger-600'
        }`}>
          <TrendIcon className="w-4 h-4" />
          <span>{change}</span>
        </div>
      </div>
      
      <div className="mt-4">
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-600 mt-1">{title}</p>
        <p className="text-xs text-gray-500 mt-1">{period}</p>
        <div className="absolute top-2 right-2">
          <Info className="w-4 h-4 text-gray-400 hover:text-primary-500" />
        </div>
      </div>
      
      {/* Details popup */}
      {showDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={(e) => e.stopPropagation()}>
          <div className="bg-white rounded-lg p-6 max-w-md w-full m-4 relative">
            <button 
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
              onClick={(e) => {
                e.stopPropagation();
                setShowDetails(false);
              }}
            >
              <X className="w-5 h-5" />
            </button>
            
            <h3 className="text-xl font-bold text-gray-900 mb-2">{title} Details</h3>
            <p className="text-3xl font-bold text-primary-600 mb-4">{value}</p>
            
            <div className="my-4 py-4 border-t border-b border-gray-200">
              <div className="flex justify-between mb-2">
                <span className="text-gray-600">Current period:</span>
                <span className="font-medium">{period}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span className="text-gray-600">Change:</span>
                <span className={`font-medium ${
                  isPositive ? 'text-success-600' : 'text-danger-600'
                }`}>{change}</span>
              </div>
            </div>
            
            <p className="text-gray-700 text-sm mb-4">{detailsInfo}</p>
            
            <button 
              className="w-full py-2 px-4 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium"
              onClick={() => alert(`Navigating to detailed ${title} analytics`)}
            >
              View Full Analytics
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MetricCard;