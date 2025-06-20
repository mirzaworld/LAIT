/**
 * LAIT API Diagnostics Tool
 * This script tests all critical API endpoints to ensure proper connectivity
 */

const API_BASE = 'http://localhost:5003';

async function testEndpoint(endpoint, options = {}) {
  const { method = 'GET', body = null, description } = options;
  console.log(`\n🔍 Testing: ${description || endpoint}`);
  
  try {
    const fetchOptions = {
      method,
      headers: { 'Content-Type': 'application/json' }
    };
    
    if (body) {
      fetchOptions.body = JSON.stringify(body);
    }
    
    const start = Date.now();
    const response = await fetch(`${API_BASE}${endpoint}`, fetchOptions);
    const elapsed = Date.now() - start;
    
    const status = response.status;
    const statusText = response.statusText;
    
    console.log(`  Status: ${status} ${statusText} (${elapsed}ms)`);
    
    if (response.ok) {
      const data = await response.json();
      console.log('  ✅ SUCCESS');
      return { success: true, data, elapsed };
    } else {
      const text = await response.text();
      console.log(`  ❌ FAILED: ${text}`);
      return { success: false, error: text, status, elapsed };
    }
  } catch (error) {
    console.log(`  ❌ ERROR: ${error.message}`);
    return { success: false, error: error.message, elapsed: 0 };
  }
}

async function runDiagnostics() {
  console.log('🚀 Starting LAIT API Diagnostics...');
  console.log('=' .repeat(50));
  
  const results = {};
  
  // Core endpoints
  results.health = await testEndpoint('/api/health', { description: 'Health Check' });
  
  // Dashboard & Metrics
  results.metrics = await testEndpoint('/api/dashboard/metrics', { description: 'Dashboard Metrics' });
  
  // Invoices
  results.invoices = await testEndpoint('/api/invoices', { description: 'Invoice List' });
  
  // Matters
  results.matters = await testEndpoint('/api/matters', { description: 'Matters List' });
  
  // Vendors
  results.vendors = await testEndpoint('/api/vendors', { description: 'Vendors List' });
  
  // ML Features
  results.ml_test = await testEndpoint('/api/ml/test', { description: 'ML Status Check' });
  results.anomalies = await testEndpoint('/api/ml/anomaly-detection', { 
    method: 'POST', 
    body: {}, 
    description: 'ML Anomaly Detection' 
  });
  
  // Workflows
  results.workflows = await testEndpoint('/api/workflow/electronic-billing', { description: 'Workflow Status' });
  
  console.log('\n\n' + '='.repeat(50));
  console.log('📊 SUMMARY REPORT');
  console.log('='.repeat(50));
  
  let success = 0;
  let failed = 0;
  
  Object.entries(results).forEach(([key, result]) => {
    const status = result.success ? '✅' : '❌';
    const time = result.elapsed ? `${result.elapsed}ms` : 'N/A';
    console.log(`${status} ${key.padEnd(20)} ${time}`);
    
    if (result.success) success++;
    else failed++;
  });
  
  console.log('='.repeat(50));
  console.log(`🔍 Results: ${success} passed, ${failed} failed`);
  
  if (failed > 0) {
    console.log(`\n❗ ${failed} endpoints are not working properly. Check the backend server.`);
    console.log('📋 Suggestions:');
    console.log('  1. Ensure backend is running on http://localhost:5003');
    console.log('  2. Check for console errors in backend');
    console.log('  3. Verify all required endpoints are implemented');
  } else {
    console.log('\n🎉 All API endpoints are working correctly!');
  }
}

// Run diagnostics
runDiagnostics().catch(console.error);
