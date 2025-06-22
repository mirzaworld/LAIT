import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertTriangle, RefreshCw, Play, FileText, Users, TrendingUp } from 'lucide-react';
import SmartButton from './SmartButton';
import toast from 'react-hot-toast';

interface TestResult {
  name: string;
  status: 'pending' | 'running' | 'success' | 'error';
  message?: string;
  details?: any;
  duration?: number;
}

const ComprehensiveSystemTest: React.FC = () => {
  const [tests, setTests] = useState<TestResult[]>([
    { name: 'Backend Health Check', status: 'pending' },
    { name: 'ML Models Availability', status: 'pending' },
    { name: 'Invoice Analyzer Test', status: 'pending' },
    { name: 'Vendor Analyzer Test', status: 'pending' },
    { name: 'Risk Predictor Test', status: 'pending' },
    { name: 'Web Data Extraction Test', status: 'pending' },
    { name: 'Database Connectivity', status: 'pending' },
    { name: 'API Endpoints Test', status: 'pending' },
  ]);

  const [isRunning, setIsRunning] = useState(false);
  const [currentTest, setCurrentTest] = useState<string | null>(null);

  const updateTestStatus = (testName: string, updates: Partial<TestResult>) => {
    setTests(prev => prev.map(test => 
      test.name === testName ? { ...test, ...updates } : test
    ));
  };

  const runTest = async (testName: string, testFn: () => Promise<any>) => {
    setCurrentTest(testName);
    updateTestStatus(testName, { status: 'running' });
    
    const startTime = Date.now();
    
    try {
      const result = await testFn();
      const duration = Date.now() - startTime;
      
      updateTestStatus(testName, {
        status: 'success',
        message: 'Test passed',
        details: result,
        duration
      });
    } catch (error: any) {
      const duration = Date.now() - startTime;
      
      updateTestStatus(testName, {
        status: 'error',
        message: error.message || 'Test failed',
        details: error,
        duration
      });
    }
  };

  const runAllTests = async () => {
    setIsRunning(true);
    setCurrentTest(null);

    // Reset all tests
    setTests(prev => prev.map(test => ({ ...test, status: 'pending' as const })));

    try {
      // Test 1: Backend Health Check
      await runTest('Backend Health Check', async () => {
        const response = await fetch('/api/health');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
      });

      // Test 2: ML Models Availability
      await runTest('ML Models Availability', async () => {
        const response = await fetch('/api/ml/test');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (!data.ml_available) throw new Error('ML models not available');
        return data;
      });

      // Test 3: Invoice Analyzer Test
      await runTest('Invoice Analyzer Test', async () => {
        const testInvoice = {
          amount: 50000,
          line_items: [
            {
              description: 'Legal research and analysis',
              hours: 10,
              rate: 500,
              amount: 5000,
              timekeeper: 'Senior Partner'
            }
          ]
        };

        const response = await fetch('/api/invoices/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(testInvoice)
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
      });

      // Test 4: Vendor Analyzer Test
      await runTest('Vendor Analyzer Test', async () => {
        const response = await fetch('/api/vendors/analytics');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
      });

      // Test 5: Risk Predictor Test
      await runTest('Risk Predictor Test', async () => {
        const testData = {
          amount: 25000,
          timekeeper_count: 3,
          line_item_count: 5,
          avg_rate: 450
        };

        const response = await fetch('/api/analytics/risk-prediction', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(testData)
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
      });

      // Test 6: Web Data Extraction Test
      await runTest('Web Data Extraction Test', async () => {
        const response = await fetch('/api/ml/extract-web-data', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: 'https://example.com/legal-document' })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
      });

      // Test 7: Database Connectivity
      await runTest('Database Connectivity', async () => {
        const response = await fetch('/api/dashboard/metrics');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
      });

      // Test 8: API Endpoints Test
      await runTest('API Endpoints Test', async () => {
        const endpoints = [
          '/api/invoices',
          '/api/vendors',
          '/api/analytics/spend-trends'
        ];

        const results = [];
        for (const endpoint of endpoints) {
          const response = await fetch(endpoint);
          results.push({
            endpoint,
            status: response.status,
            ok: response.ok
          });
        }

        return results;
      });

      toast.success('All tests completed!');
    } catch (error) {
      toast.error('Test suite interrupted');
      console.error('Test suite error:', error);
    } finally {
      setIsRunning(false);
      setCurrentTest(null);
    }
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'running':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getTestIcon = (testName: string) => {
    if (testName.includes('Invoice')) return <FileText className="w-4 h-4" />;
    if (testName.includes('Vendor')) return <Users className="w-4 h-4" />;
    if (testName.includes('Risk')) return <TrendingUp className="w-4 h-4" />;
    return <Play className="w-4 h-4" />;
  };

  const successCount = tests.filter(t => t.status === 'success').length;
  const errorCount = tests.filter(t => t.status === 'error').length;
  const pendingCount = tests.filter(t => t.status === 'pending').length;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">System Comprehensive Test</h3>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-600">
            ✅ {successCount} | ❌ {errorCount} | ⏳ {pendingCount}
          </div>
          <SmartButton
            onClick={runAllTests}
            disabled={isRunning}
            loading={isRunning}
            variant="primary"
          >
            {isRunning ? 'Running Tests...' : 'Run All Tests'}
          </SmartButton>
        </div>
      </div>

      <div className="space-y-3">
        {tests.map((test, index) => (
          <div
            key={test.name}
            className={`flex items-center justify-between p-4 rounded-lg border ${
              test.status === 'running'
                ? 'border-blue-200 bg-blue-50'
                : test.status === 'success'
                ? 'border-green-200 bg-green-50'
                : test.status === 'error'
                ? 'border-red-200 bg-red-50'
                : 'border-gray-200 bg-gray-50'
            }`}
          >
            <div className="flex items-center space-x-3">
              {getTestIcon(test.name)}
              <div>
                <div className="font-medium text-gray-900">{test.name}</div>
                {test.message && (
                  <div className={`text-sm ${
                    test.status === 'error' ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {test.message}
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {test.duration && (
                <span className="text-xs text-gray-500">
                  {test.duration}ms
                </span>
              )}
              {getStatusIcon(test.status)}
            </div>
          </div>
        ))}
      </div>

      {currentTest && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />
            <span className="text-sm font-medium text-blue-700">
              Currently running: {currentTest}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComprehensiveSystemTest;
