import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { Brain, TrendingUp, AlertTriangle, Users, FileText, Globe, RefreshCw } from 'lucide-react';
import SmartButton from './SmartButton';
import toast from 'react-hot-toast';

interface MLAnalyticsData {
  riskAnalysis: {
    highRisk: number;
    mediumRisk: number;
    lowRisk: number;
  };
  vendorInsights: Array<{
    vendor: string;
    riskScore: number;
    cluster: number;
    performance: number;
  }>;
  invoicePatterns: Array<{
    month: string;
    anomalies: number;
    totalInvoices: number;
    avgRisk: number;
  }>;
  webExtractionStats: {
    documentsProcessed: number;
    entitiesExtracted: number;
    avgConfidence: number;
  };
}

const MLPoweredAnalytics: React.FC = () => {
  const [data, setData] = useState<MLAnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeModel, setActiveModel] = useState<string>('all');
  const [webUrl, setWebUrl] = useState('');
  const [webExtractionResult, setWebExtractionResult] = useState<any>(null);

  const fetchMLAnalytics = async () => {
    setLoading(true);
    try {
      // First test if ML models are available
      const mlTestResponse = await fetch('/api/ml/test');
      const mlTestData = await mlTestResponse.json();
      
      if (!mlTestData.ml_available) {
        toast.error('ML models are not available');
        return;
      }

      // Simulate comprehensive ML analytics (in production, these would be real API calls)
      const mockData: MLAnalyticsData = {
        riskAnalysis: {
          highRisk: 15,
          mediumRisk: 45,
          lowRisk: 140
        },
        vendorInsights: [
          { vendor: 'Law Firm A', riskScore: 0.8, cluster: 2, performance: 85 },
          { vendor: 'Law Firm B', riskScore: 0.3, cluster: 1, performance: 92 },
          { vendor: 'Law Firm C', riskScore: 0.6, cluster: 2, performance: 78 },
          { vendor: 'Legal Services Inc', riskScore: 0.2, cluster: 0, performance: 95 },
        ],
        invoicePatterns: [
          { month: 'Jan', anomalies: 5, totalInvoices: 45, avgRisk: 0.3 },
          { month: 'Feb', anomalies: 8, totalInvoices: 52, avgRisk: 0.4 },
          { month: 'Mar', anomalies: 3, totalInvoices: 38, avgRisk: 0.2 },
          { month: 'Apr', anomalies: 12, totalInvoices: 67, avgRisk: 0.5 },
          { month: 'May', anomalies: 6, totalInvoices: 41, avgRisk: 0.3 },
          { month: 'Jun', anomalies: 9, totalInvoices: 58, avgRisk: 0.4 },
        ],
        webExtractionStats: {
          documentsProcessed: 1247,
          entitiesExtracted: 8934,
          avgConfidence: 0.87
        }
      };

      setData(mockData);
      toast.success('ML analytics loaded successfully');
    } catch (error) {
      console.error('Error fetching ML analytics:', error);
      toast.error('Failed to load ML analytics');
    } finally {
      setLoading(false);
    }
  };

  const testWebExtraction = async () => {
    if (!webUrl) {
      toast.error('Please enter a URL');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/ml/extract-web-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: webUrl })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();
      setWebExtractionResult(result);
      toast.success('Web data extracted successfully');
    } catch (error: any) {
      console.error('Web extraction error:', error);
      toast.error(`Web extraction failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const retrainModels = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ml/retrain', { method: 'POST' });
      const result = await response.json();
      
      if (response.ok) {
        toast.success('ML models retrained successfully');
        fetchMLAnalytics(); // Refresh data
      } else {
        toast.error(result.message || 'Failed to retrain models');
      }
    } catch (error) {
      console.error('Retrain error:', error);
      toast.error('Failed to retrain ML models');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMLAnalytics();
  }, []);

  const COLORS = ['#3B82F6', '#EF4444', '#F59E0B', '#10B981'];

  const riskPieData = data ? [
    { name: 'Low Risk', value: data.riskAnalysis.lowRisk, color: '#10B981' },
    { name: 'Medium Risk', value: data.riskAnalysis.mediumRisk, color: '#F59E0B' },
    { name: 'High Risk', value: data.riskAnalysis.highRisk, color: '#EF4444' },
  ] : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Brain className="w-8 h-8 text-blue-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">ML-Powered Analytics</h2>
              <p className="text-gray-600">Advanced analytics using machine learning models</p>
            </div>
          </div>
          <div className="flex space-x-2">
            <SmartButton
              onClick={fetchMLAnalytics}
              loading={loading}
              variant="secondary"
              size="sm"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </SmartButton>
            <SmartButton
              onClick={retrainModels}
              loading={loading}
              variant="primary"
              size="sm"
            >
              Retrain Models
            </SmartButton>
          </div>
        </div>
      </div>

      {data && (
        <>
          {/* Risk Analysis Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <AlertTriangle className="w-5 h-5 text-yellow-500 mr-2" />
                Risk Distribution
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={riskPieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {riskPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 text-green-500 mr-2" />
                Invoice Anomaly Trends
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data.invoicePatterns}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="anomalies" stroke="#EF4444" name="Anomalies" />
                  <Line type="monotone" dataKey="avgRisk" stroke="#F59E0B" name="Avg Risk" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Vendor Analysis */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Users className="w-5 h-5 text-blue-500 mr-2" />
              Vendor Risk & Performance Analysis
            </h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={data.vendorInsights}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="vendor" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="riskScore" fill="#EF4444" name="Risk Score" />
                <Bar dataKey="performance" fill="#10B981" name="Performance %" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Web Data Extraction */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Globe className="w-5 h-5 text-purple-500 mr-2" />
              Web Data Extraction ML
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {data.webExtractionStats.documentsProcessed.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Documents Processed</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {data.webExtractionStats.entitiesExtracted.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Entities Extracted</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {(data.webExtractionStats.avgConfidence * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Average Confidence</div>
              </div>
            </div>

            <div className="flex space-x-2 mb-4">
              <input
                type="url"
                value={webUrl}
                onChange={(e) => setWebUrl(e.target.value)}
                placeholder="Enter URL to extract legal data"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <SmartButton
                onClick={testWebExtraction}
                loading={loading}
                variant="primary"
              >
                Extract Data
              </SmartButton>
            </div>

            {webExtractionResult && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Extraction Results:</h4>
                <div className="text-sm text-gray-600 space-y-2">
                  <div><strong>Title:</strong> {webExtractionResult.data.title}</div>
                  <div><strong>Content Type:</strong> {webExtractionResult.data.content_type}</div>
                  <div><strong>ML Confidence:</strong> {(webExtractionResult.data.ml_confidence * 100).toFixed(1)}%</div>
                  
                  <div>
                    <strong>Key Facts:</strong>
                    <ul className="list-disc list-inside ml-2">
                      {webExtractionResult.data.key_facts.map((fact: string, index: number) => (
                        <li key={index}>{fact}</li>
                      ))}
                    </ul>
                  </div>

                  {webExtractionResult.data.risk_analysis && (
                    <div>
                      <strong>AI Risk Analysis:</strong> Risk Score {webExtractionResult.data.risk_analysis.risk_score || 'N/A'}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {!data && !loading && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">ML Analytics Not Loaded</h3>
          <p className="text-gray-600 mb-4">Click the button below to load ML-powered analytics</p>
          <SmartButton onClick={fetchMLAnalytics} variant="primary">
            Load ML Analytics
          </SmartButton>
        </div>
      )}
    </div>
  );
};

export default MLPoweredAnalytics;
