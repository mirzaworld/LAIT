#!/usr/bin/env node

/**
 * Comprehensive Integration Test Suite for LAIT Platform
 * Tests the entire system end-to-end including frontend, backend, and ML models
 */

const axios = require('axios');
const { exec } = require('child_process');
const fs = require('fs');

// Configuration
const BACKEND_URL = 'http://localhost:5003';
const FRONTEND_URL = 'http://localhost:3000';
const TEST_TIMEOUT = 30000;

// Test results tracking
let testResults = {
  passed: 0,
  failed: 0,
  total: 0,
  details: []
};

// Utility functions
const log = (message, type = 'INFO') => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] [${type}] ${message}`);
};

const test = async (name, testFunction) => {
  testResults.total++;
  log(`Running test: ${name}`, 'TEST');
  
  try {
    await testFunction();
    testResults.passed++;
    log(`✅ PASSED: ${name}`, 'PASS');
    testResults.details.push({ name, status: 'PASSED', error: null });
  } catch (error) {
    testResults.failed++;
    log(`❌ FAILED: ${name} - ${error.message}`, 'FAIL');
    testResults.details.push({ name, status: 'FAILED', error: error.message });
  }
};

// Health check tests
const testBackendHealth = async () => {
  const response = await axios.get(`${BACKEND_URL}/api/health`, { timeout: TEST_TIMEOUT });
  if (response.status !== 200) throw new Error(`Expected 200, got ${response.status}`);
  if (response.data.status !== 'healthy') throw new Error('Backend not healthy');
};

const testFrontendHealth = async () => {
  const response = await axios.get(FRONTEND_URL, { timeout: TEST_TIMEOUT });
  if (response.status !== 200) throw new Error(`Expected 200, got ${response.status}`);
};

// API endpoint tests
const testLegalIntelligenceAPI = async () => {
  const response = await axios.get(`${BACKEND_URL}/api/legal-intelligence/test`, { timeout: TEST_TIMEOUT });
  if (response.status !== 200) throw new Error(`Expected 200, got ${response.status}`);
  if (response.data.status !== 'success') throw new Error('Legal intelligence API not working');
  
  // Test attorney verification
  const verifyResponse = await axios.post(`${BACKEND_URL}/api/legal-intelligence/verify-attorney`, {
    attorney_name: 'John Smith',
    law_firm: 'Test Law Firm',
    bar_number: '12345',
    state: 'CA'
  }, { timeout: TEST_TIMEOUT });
  
  if (verifyResponse.status !== 200) throw new Error('Attorney verification failed');
  if (!verifyResponse.data.hasOwnProperty('verified')) throw new Error('Invalid attorney verification response');
};

const testMLModelsAPI = async () => {
  const response = await axios.get(`${BACKEND_URL}/api/ml/status`, { timeout: TEST_TIMEOUT });
  if (response.status !== 200) throw new Error(`Expected 200, got ${response.status}`);
  
  const requiredModels = ['enhanced_invoice_analyzer', 'invoice_analyzer', 'matter_analyzer', 'risk_predictor', 'vendor_analyzer'];
  for (const model of requiredModels) {
    if (!response.data.models[model]) throw new Error(`ML model ${model} not loaded`);
  }
};

const testAnalyticsAPI = async () => {
  const response = await axios.get(`${BACKEND_URL}/api/analytics/dashboard/metrics`, { timeout: TEST_TIMEOUT });
  if (response.status !== 200) throw new Error(`Expected 200, got ${response.status}`);
  
  const requiredFields = ['totalSpend', 'invoiceCount', 'vendorCount', 'averageRiskScore'];
  for (const field of requiredFields) {
    if (!response.data.hasOwnProperty(field)) throw new Error(`Missing field: ${field}`);
  }
};

const testVendorAPI = async () => {
  const response = await axios.get(`${BACKEND_URL}/api/vendors`, { timeout: TEST_TIMEOUT });
  if (response.status !== 200) throw new Error(`Expected 200, got ${response.status}`);
  if (!response.data.vendors) throw new Error('Vendor API response missing vendors array');
};

const testInvoiceAPI = async () => {
  const response = await axios.get(`${BACKEND_URL}/api/invoices`, { timeout: TEST_TIMEOUT });
  if (response.status !== 200) throw new Error(`Expected 200, got ${response.status}`);
  if (!Array.isArray(response.data) && !response.data.invoices) throw new Error('Invoice API response format invalid');
};

// Performance tests
const testAPIPerformance = async () => {
  const startTime = Date.now();
  await axios.get(`${BACKEND_URL}/api/health`, { timeout: TEST_TIMEOUT });
  const responseTime = Date.now() - startTime;
  
  if (responseTime > 1000) throw new Error(`API response too slow: ${responseTime}ms`);
};

const testMLModelPerformance = async () => {
  const startTime = Date.now();
  await axios.get(`${BACKEND_URL}/api/ml/status`, { timeout: TEST_TIMEOUT });
  const responseTime = Date.now() - startTime;
  
  if (responseTime > 2000) throw new Error(`ML status response too slow: ${responseTime}ms`);
};

// Error handling tests
const testErrorHandling = async () => {
  try {
    await axios.get(`${BACKEND_URL}/api/nonexistent`, { timeout: TEST_TIMEOUT });
    throw new Error('Expected 404 error for nonexistent endpoint');
  } catch (error) {
    if (error.response && error.response.status === 404) {
      // Expected behavior
      return;
    }
    throw new Error(`Unexpected error handling: ${error.message}`);
  }
};

// Data consistency tests
const testDataConsistency = async () => {
  // Test that analytics data is consistent
  const analyticsResponse = await axios.get(`${BACKEND_URL}/api/analytics/dashboard/metrics`, { timeout: TEST_TIMEOUT });
  const vendorResponse = await axios.get(`${BACKEND_URL}/api/vendors`, { timeout: TEST_TIMEOUT });
  
  if (analyticsResponse.data.vendorCount !== vendorResponse.data.vendors.length) {
    throw new Error('Vendor count mismatch between analytics and vendor API');
  }
};

// Frontend integration tests
const testFrontendBackendIntegration = async () => {
  // Test that frontend can access backend APIs through proxy
  const response = await axios.get(`${FRONTEND_URL}/api/health`, { timeout: TEST_TIMEOUT });
  if (response.status !== 200) throw new Error('Frontend-backend proxy not working');
};

// Main test runner
const runAllTests = async () => {
  log('🚀 Starting Comprehensive Integration Tests', 'START');
  log(`Backend URL: ${BACKEND_URL}`, 'CONFIG');
  log(`Frontend URL: ${FRONTEND_URL}`, 'CONFIG');
  
  // Health checks
  await test('Backend Health Check', testBackendHealth);
  await test('Frontend Health Check', testFrontendHealth);
  
  // API functionality tests
  await test('Legal Intelligence API', testLegalIntelligenceAPI);
  await test('ML Models API', testMLModelsAPI);
  await test('Analytics API', testAnalyticsAPI);
  await test('Vendor API', testVendorAPI);
  await test('Invoice API', testInvoiceAPI);
  
  // Performance tests
  await test('API Performance', testAPIPerformance);
  await test('ML Model Performance', testMLModelPerformance);
  
  // Error handling tests
  await test('Error Handling', testErrorHandling);
  
  // Data consistency tests
  await test('Data Consistency', testDataConsistency);
  
  // Integration tests
  await test('Frontend-Backend Integration', testFrontendBackendIntegration);
  
  // Generate test report
  generateTestReport();
};

const generateTestReport = () => {
  log('\n📊 TEST RESULTS SUMMARY', 'REPORT');
  log(`Total Tests: ${testResults.total}`, 'REPORT');
  log(`Passed: ${testResults.passed}`, 'REPORT');
  log(`Failed: ${testResults.failed}`, 'REPORT');
  log(`Success Rate: ${((testResults.passed / testResults.total) * 100).toFixed(1)}%`, 'REPORT');
  
  if (testResults.failed > 0) {
    log('\n❌ FAILED TESTS:', 'REPORT');
    testResults.details
      .filter(result => result.status === 'FAILED')
      .forEach(result => {
        log(`  - ${result.name}: ${result.error}`, 'REPORT');
      });
  }
  
  // Save detailed report
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      total: testResults.total,
      passed: testResults.passed,
      failed: testResults.failed,
      successRate: (testResults.passed / testResults.total) * 100
    },
    details: testResults.details
  };
  
  fs.writeFileSync('integration_test_report.json', JSON.stringify(report, null, 2));
  log('📄 Detailed report saved to integration_test_report.json', 'REPORT');
  
  // Exit with appropriate code
  process.exit(testResults.failed > 0 ? 1 : 0);
};

// Run tests
runAllTests().catch(error => {
  log(`💥 Test runner failed: ${error.message}`, 'ERROR');
  process.exit(1);
}); 