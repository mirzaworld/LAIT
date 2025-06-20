// Quick test script to verify API endpoints
const baseURL = 'http://localhost:8000/api';
const token = 'mock-jwt-token-for-development';

async function testEndpoint(url, name) {
  try {
    const response = await fetch(`${baseURL}${url}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log(`✅ ${name}: Working`);
      console.log(`   First item:`, Object.keys(data)[0], ':', Object.values(data)[0]);
    } else {
      console.log(`❌ ${name}: Failed with status ${response.status}`);
    }
  } catch (error) {
    console.log(`❌ ${name}: Error -`, error.message);
  }
}

async function runTests() {
  console.log('Testing LAIT API endpoints...\n');
  
  await testEndpoint('/analytics/summary', 'Dashboard Metrics');
  await testEndpoint('/invoices?limit=3', 'Invoices');
  await testEndpoint('/vendors?limit=3', 'Vendors');
  await testEndpoint('/analytics/spend-trends', 'Spend Trends');
  
  console.log('\n✨ API Test Complete!');
}

runTests();
