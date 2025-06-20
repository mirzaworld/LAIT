#!/usr/bin/env node
/**
 * LAIT - Enhanced Legal Intelligence System
 * Comprehensive Integration Test
 * 
 * This script tests the connection between the frontend and backend
 * by verifying all critical API endpoints.
 */

// Configuration
const API_URL = process.env.VITE_API_URL || 'http://localhost:5003/api';
const token = 'mock-jwt-token-for-development';

// Terminal colors for better output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

// Helper function to create a spacer
const spacer = () => console.log('\n' + '-'.repeat(60) + '\n');

// Test a single API endpoint
async function testEndpoint(url, name, options = {}) {
  process.stdout.write(`Testing ${colors.cyan}${name}${colors.reset}... `);
  try {
    // Add authorization header if needed
    const headers = {
      'Content-Type': 'application/json',
      ...(options.auth && { 'Authorization': `Bearer ${token}` }),
    };

    const fetchOptions = {
      method: options.method || 'GET',
      headers,
      ...(options.body && { body: JSON.stringify(options.body) }),
    };

    const response = await fetch(`${API_URL}${url}`, fetchOptions);
    
    if (response.ok) {
      const data = await response.json();
      console.log(`${colors.green}✓ SUCCESS${colors.reset}`);
      
      if (options.verbose) {
        console.log(`${colors.yellow}Response:${colors.reset}`, 
          JSON.stringify(data).substring(0, 200) + (JSON.stringify(data).length > 200 ? '...' : ''));
      }
      
      return { success: true, data };
    } else {
      console.log(`${colors.red}✗ FAILED (Status: ${response.status})${colors.reset}`);
      return { 
        success: false, 
        status: response.status, 
        statusText: response.statusText 
      };
    }
  } catch (error) {
    console.log(`${colors.red}✗ ERROR: ${error.message}${colors.reset}`);
    return { success: false, error: error.message };
  }
}

// Main test runner
async function runTests() {
  console.log(`\n${colors.blue}=== LAIT INTEGRATION TEST ====${colors.reset}`);
  console.log(`${colors.yellow}Testing backend API at: ${API_URL}${colors.reset}\n`);
  
  let passCount = 0;
  let failCount = 0;
  
  const testSuites = [
    {
      name: 'Core API Health',
      tests: [
        { url: '/health', name: 'API Health Check' },
        { url: '/status', name: 'API Status' },
      ]
    },
    {
      name: 'Dashboard API',
      tests: [
        { url: '/dashboard/metrics', name: 'Dashboard Metrics' },
        { url: '/dashboard/summary', name: 'Dashboard Summary' },
        { url: '/analytics/spend', name: 'Spend Analytics' },
      ]
    },
    {
      name: 'Invoices API',
      tests: [
        { url: '/invoices?limit=5', name: 'Recent Invoices' },
        { url: '/invoices/stats', name: 'Invoice Statistics' },
      ]
    },
    {
      name: 'Vendors API',
      tests: [
        { url: '/vendors/top', name: 'Top Vendors' },
        { url: '/vendors/analytics', name: 'Vendor Analytics' },
      ]
    },
    {
      name: 'Document API',
      tests: [
        { url: '/documents/types', name: 'Document Types' },
        { url: '/documents/recent', name: 'Recent Documents' },
      ]
    },
  ];

  for (const suite of testSuites) {
    spacer();
    console.log(`${colors.magenta}## ${suite.name} ##${colors.reset}\n`);
    
    for (const test of suite.tests) {
      const result = await testEndpoint(test.url, test.name, { verbose: true });
      
      if (result.success) {
        passCount++;
      } else {
        failCount++;
      }
    }
  }
  
  spacer();
  console.log(`${colors.blue}=== TEST SUMMARY ====${colors.reset}`);
  console.log(`${colors.green}Tests Passed: ${passCount}${colors.reset}`);
  console.log(`${colors.red}Tests Failed: ${failCount}${colors.reset}`);
  console.log(`${colors.yellow}Total Tests: ${passCount + failCount}${colors.reset}\n`);
  
  if (failCount === 0) {
    console.log(`${colors.green}✅ All tests passed! The LAIT system is functioning correctly.${colors.reset}\n`);
    return true;
  } else {
    const passRate = Math.round((passCount / (passCount + failCount)) * 100);
    console.log(`${colors.yellow}⚠️ Some tests failed. Pass rate: ${passRate}%${colors.reset}`);
    console.log(`${colors.yellow}Review the test output above for details.${colors.reset}\n`);
    return false;
  }
}

runTests().then(success => {
  if (!success) {
    process.exit(1);
  }
});
