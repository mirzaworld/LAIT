import React, { useState, useEffect } from 'react';
import { TrendingUp, Brain, Target, Users, AlertTriangle, CheckCircle, BarChart3, PieChart } from 'lucide-react';

const AdvancedAnalytics: React.FC = () => {
  const [predictiveData, setPredictiveData] = useState<any>(null);
  const [vendorPerformance, setVendorPerformance] = useState<any>(null);
  const [budgetForecast, setBudgetForecast] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5003/api';
        
        // Fetch advanced analytics with fallback data
        try {
          const predictiveRes = await fetch(`${API_URL}/analytics/predictive`);
          if (predictiveRes.ok) {
            setPredictiveData(await predictiveRes.json());
          } else {
            console.log('Using fallback predictive data');
            setPredictiveData({
              predictions: [
                { category: 'Legal Spend', current: 100000, predicted: 120000 },
                { category: 'Case Load', current: 50, predicted: 65 }
              ],
              confidence: 0.85
            });
          }
        } catch (error) {
          console.error('Error fetching predictive analytics:', error);
        }

        try {
          const vendorRes = await fetch(`${API_URL}/analytics/vendor-performance`);
          if (vendorRes.ok) {
            setVendorPerformance(await vendorRes.json());
          } else {
            console.log('Using fallback vendor data');
            setVendorPerformance({
              vendors: [
                { name: 'Firm A', performance: 0.85, trend: 'up' },
                { name: 'Firm B', performance: 0.75, trend: 'stable' }
              ]
            });
          }
        } catch (error) {
          console.error('Error fetching vendor analytics:', error);
        }

        try {
          const budgetRes = await fetch(`${API_URL}/analytics/budget-forecast`);
          if (budgetRes.ok) {
            setBudgetForecast(await budgetRes.json());
          } else {
            console.log('Using fallback budget data');
            setBudgetForecast({
              currentSpend: 500000,
              projectedSpend: 550000,
              trends: [
                { month: 'Jan', actual: 40000, projected: 42000 },
                { month: 'Feb', actual: 45000, projected: 44000 }
              ]
            });
          }
        } catch (error) {
          console.error('Error fetching budget forecast:', error);
        }

        // State is set in individual try/catch blocks above
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load analytics');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2">Loading advanced analytics...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-danger-50 text-danger-700 p-4 rounded-lg flex items-center">
        <AlertTriangle className="w-5 h-5 mr-2" />
        <div>
          <p className="font-medium">Error loading analytics</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Advanced Analytics</h1>
          <p className="text-gray-600">AI-powered insights and predictive analysis</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-primary-600">
          <Brain className="w-4 h-4" />
          <span>Powered by AI/ML Models</span>
        </div>
      </div>

      {/* Predictive Analytics Section */}
      {predictiveData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Next Month Prediction */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center mb-4">
              <TrendingUp className="w-5 h-5 text-primary-600 mr-2" />
              <h3 className="text-lg font-semibold">Spending Forecast</h3>
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Next Month Prediction</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(predictiveData.predictions.next_month_spend.amount)}
                </p>
                <div className="flex items-center mt-1">
                  <span className={`text-sm px-2 py-1 rounded-full ${
                    predictiveData.predictions.next_month_spend.trend === 'increasing' 
                      ? 'bg-danger-100 text-danger-700' 
                      : predictiveData.predictions.next_month_spend.trend === 'decreasing'
                      ? 'bg-success-100 text-success-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}>
                    {predictiveData.predictions.next_month_spend.trend}
                  </span>
                  <span className="text-sm text-gray-500 ml-2">
                    {Math.round(predictiveData.predictions.next_month_spend.confidence * 100)}% confidence
                  </span>
                </div>
              </div>
              
              <div className="border-t pt-4">
                <p className="text-sm font-medium text-gray-900">Budget Alert</p>
                <p className="text-sm text-gray-600 mt-1">
                  {predictiveData.predictions.budget_alert.message}
                </p>
                <p className="text-xs text-primary-600 mt-2">
                  💡 {predictiveData.predictions.budget_alert.recommended_action}
                </p>
              </div>
            </div>
          </div>

          {/* AI Insights */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center mb-4">
              <Brain className="w-5 h-5 text-purple-600 mr-2" />
              <h3 className="text-lg font-semibold">AI Insights</h3>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-900">Compliance Score</p>
                <div className="flex items-center mt-1">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-success-500 h-2 rounded-full" 
                      style={{width: `${predictiveData.ai_insights.compliance_score}%`}}
                    ></div>
                  </div>
                  <span className="ml-3 text-sm font-semibold">
                    {predictiveData.ai_insights.compliance_score}%
                  </span>
                </div>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-900">Efficiency Rating</p>
                <span className="inline-block px-3 py-1 bg-success-100 text-success-700 rounded-full text-sm font-medium">
                  {predictiveData.ai_insights.efficiency_rating}
                </span>
              </div>
              
              <div className="border-t pt-3">
                <p className="text-sm font-medium text-gray-900 mb-2">Recommendations</p>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• {predictiveData.ai_insights.cost_optimization}</li>
                  <li>• {predictiveData.ai_insights.process_improvement}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Vendor Performance Analysis */}
      {vendorPerformance && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <Users className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold">Vendor Performance Analysis</h3>
            </div>
            <div className="text-sm text-gray-500">
              {vendorPerformance.summary.total_vendors} vendors analyzed
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Vendor</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Performance Score</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Total Spend</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Risk Score</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Rating</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {vendorPerformance.vendor_performance.slice(0, 5).map((vendor: any, index: number) => (
                  <tr key={index} className="border-b border-gray-100">
                    <td className="py-3 px-4 font-medium">{vendor.vendor}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3" style={{width: '80px'}}>
                          <div 
                            className={`h-2 rounded-full ${
                              vendor.performance_score > 90 ? 'bg-success-500' :
                              vendor.performance_score > 80 ? 'bg-warning-500' :
                              'bg-danger-500'
                            }`}
                            style={{width: `${vendor.performance_score}%`}}
                          ></div>
                        </div>
                        <span className="text-sm font-semibold">{vendor.performance_score}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">{formatCurrency(vendor.total_spend)}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        vendor.avg_risk_score > 70 ? 'bg-danger-100 text-danger-700' :
                        vendor.avg_risk_score > 40 ? 'bg-warning-100 text-warning-700' :
                        'bg-success-100 text-success-700'
                      }`}>
                        {vendor.avg_risk_score}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        vendor.efficiency_rating === 'A' ? 'bg-success-100 text-success-700' :
                        vendor.efficiency_rating === 'B' ? 'bg-warning-100 text-warning-700' :
                        'bg-danger-100 text-danger-700'
                      }`}>
                        {vendor.efficiency_rating}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">{vendor.recommendation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Budget Forecast */}
      {budgetForecast && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-6">
            <Target className="w-5 h-5 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold">Budget Forecast & Scenarios</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Annual Projection</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(budgetForecast.forecast.annual_projection)}
              </p>
              <p className="text-sm text-gray-500">Base scenario</p>
            </div>
            
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Optimistic</p>
              <p className="text-xl font-bold text-success-600">
                {formatCurrency(budgetForecast.forecast.confidence_interval.optimistic)}
              </p>
              <p className="text-sm text-gray-500">With optimization</p>
            </div>
            
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Pessimistic</p>
              <p className="text-xl font-bold text-danger-600">
                {formatCurrency(budgetForecast.forecast.confidence_interval.pessimistic)}
              </p>
              <p className="text-sm text-gray-500">Market volatility</p>
            </div>
          </div>
          
          <div className="border-t pt-6">
            <h4 className="font-medium text-gray-900 mb-3">Recommendations</h4>
            <ul className="space-y-2">
              {budgetForecast.recommendations.map((rec: string, index: number) => (
                <li key={index} className="flex items-start">
                  <CheckCircle className="w-4 h-4 text-success-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedAnalytics;
