import React from 'react';
import { TrendingUp, TrendingDown, DivideIcon as LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string;
  change: string;
  changeType: 'increase' | 'decrease';
  icon: LucideIcon;
  period: string;
  index: number;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  changeType,
  icon: Icon,
  period,
  index
}) => {
  const isPositive = changeType === 'increase';
  const TrendIcon = isPositive ? TrendingUp : TrendingDown;

  return (
    <div 
      className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all duration-300 animate-slide-up"
      style={{ animationDelay: `${index * 100}ms` }}
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
      </div>
    </div>
  );
};

export default MetricCard;