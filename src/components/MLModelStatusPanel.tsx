import React, { useState, useEffect } from 'react';
import { Brain, CheckCircle, XCircle, RefreshCw, AlertTriangle, Globe } from 'lucide-react';
import toast from 'react-hot-toast';

interface MLModelStatus {
  ml_available: boolean;
  models_status: {
    invoice_analyzer?: string;
    vendor_analyzer?: string;
    risk_predictor?: string;
  };
  test_results: {
    invoice_analysis?: {
      risk_score: number;
      status: string;
    };
    vendor_analysis?: {
      risk_score: number;
      cluster: number;
      status: string;
    };
    risk_prediction?: {
      risk_score: number;
      risk_level: string;
      status: string;
    };
  };
}

const MLModelStatusPanel: React.FC = () => {
  const [status, setStatus] = useState<MLModelStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [webExtractionTest, setWebExtractionTest] = useState<any>(null);
  const [testUrl, setTestUrl] = useState('https://example.com/legal-document');

  const testMLModels = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ml/test');
      const data = await response.json();
      setStatus(data);
      
      if (data.ml_available) {
        toast.success('All ML models tested successfully!');
      } else {
        toast.error('ML models are not available');
      }
    } catch (error) {
      console.error('Error testing ML models:', error);
      toast.error('Failed to test ML models');
    } finally {
      setLoading(false);
    }
  };

  const retrainModels = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ml/retrain', { method: 'POST' });
      const data = await response.json();
      
      if (response.ok) {
        toast.success('ML models retrained successfully!');
        // Refresh status after retraining
        testMLModels();
      } else {
        toast.error(data.message || 'Failed to retrain models');
      }
    } catch (error) {
      console.error('Error retraining models:', error);
      toast.error('Failed to retrain ML models');
    } finally {
      setLoading(false);
    }
  };

  const testWebExtraction = async () => {
    if (!testUrl) {
      toast.error('Please enter a URL to test');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/ml/extract-web-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: testUrl }),
      });
      const data = await response.json();
      
      if (response.ok) {
        setWebExtractionTest(data);
        toast.success('Web data extraction successful!');
      } else {
        toast.error(data.error || 'Failed to extract web data');
      }
    } catch (error) {
      console.error('Error testing web extraction:', error);
      toast.error('Failed to test web data extraction');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testMLModels();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'working':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'not_available':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Brain className="w-6 h-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">ML Models Status</h3>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={testMLModels}
            disabled={loading}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              loading
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {loading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              'Test Models'
            )}
          </button>
          <button
            onClick={retrainModels}
            disabled={loading}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              loading
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            Retrain Models
          </button>
        </div>
      </div>

      {status && (
        <div className="space-y-4">
          {/* Overall Status */}
          <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
            {status.ml_available ? (
              <CheckCircle className="w-5 h-5 text-green-500" />
            ) : (
              <XCircle className="w-5 h-5 text-red-500" />
            )}
            <span className="text-sm font-medium">
              ML Models: {status.ml_available ? 'Available' : 'Not Available'}
            </span>
          </div>

          {/* Individual Model Status */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">Invoice Analyzer</h4>
                {getStatusIcon(status.models_status.invoice_analyzer || '')}
              </div>
              {status.test_results.invoice_analysis && (
                <div className="text-sm text-gray-600">
                  <p>Risk Score: {status.test_results.invoice_analysis.risk_score}</p>
                  <p>Status: {status.test_results.invoice_analysis.status}</p>
                </div>
              )}
            </div>

            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">Vendor Analyzer</h4>
                {getStatusIcon(status.models_status.vendor_analyzer || '')}
              </div>
              {status.test_results.vendor_analysis && (
                <div className="text-sm text-gray-600">
                  <p>Risk Score: {status.test_results.vendor_analysis.risk_score.toFixed(2)}</p>
                  <p>Cluster: {status.test_results.vendor_analysis.cluster}</p>
                  <p>Status: {status.test_results.vendor_analysis.status}</p>
                </div>
              )}
            </div>

            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">Risk Predictor</h4>
                {getStatusIcon(status.models_status.risk_predictor || '')}
              </div>
              {status.test_results.risk_prediction && (
                <div className="text-sm text-gray-600">
                  <p>Risk Score: {status.test_results.risk_prediction.risk_score}</p>
                  <p>Risk Level: {status.test_results.risk_prediction.risk_level}</p>
                  <p>Status: {status.test_results.risk_prediction.status}</p>
                </div>
              )}
            </div>
          </div>

          {/* Web Data Extraction Test */}
          <div className="mt-6 p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-4">
              <Globe className="w-5 h-5 text-purple-600" />
              <h4 className="font-medium text-gray-900">Web Data Extraction ML</h4>
            </div>
            
            <div className="flex space-x-2 mb-4">
              <input
                type="url"
                value={testUrl}
                onChange={(e) => setTestUrl(e.target.value)}
                placeholder="Enter URL to test web extraction"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={testWebExtraction}
                disabled={loading}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  loading
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-purple-600 text-white hover:bg-purple-700'
                }`}
              >
                Extract Data
              </button>
            </div>

            {webExtractionTest && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h5 className="font-medium text-gray-900 mb-2">Extraction Results:</h5>
                <div className="text-sm text-gray-600 space-y-1">
                  <p><strong>Title:</strong> {webExtractionTest.data.title}</p>
                  <p><strong>Content Type:</strong> {webExtractionTest.data.content_type}</p>
                  <p><strong>ML Confidence:</strong> {(webExtractionTest.data.ml_confidence * 100).toFixed(1)}%</p>
                  <p><strong>Processing Time:</strong> {webExtractionTest.data.processing_time}</p>
                  
                  <div className="mt-2">
                    <strong>Extracted Entities:</strong>
                    <ul className="list-disc list-inside ml-2">
                      {webExtractionTest.data.extracted_entities.map((entity: any, index: number) => (
                        <li key={index}>
                          {entity.type}: {entity.value} ({(entity.confidence * 100).toFixed(1)}%)
                        </li>
                      ))}
                    </ul>
                  </div>

                  {webExtractionTest.data.risk_analysis && (
                    <div className="mt-2">
                      <strong>Risk Analysis:</strong>
                      <p>Risk Score: {webExtractionTest.data.risk_analysis.risk_score || 'N/A'}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MLModelStatusPanel;
