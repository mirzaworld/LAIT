// Debug frontend API calls from browser context
console.log('Starting frontend API debug...');

// Test the API endpoints from the browser
async function testAPIEndpoints() {
    const API_URL = 'http://localhost:5002/api';
    
    console.log('Testing API endpoints...');
    
    try {
        // Test health endpoint
        console.log('1. Testing health endpoint...');
        const healthResponse = await fetch(`${API_URL}/health`);
        const healthData = await healthResponse.json();
        console.log('Health response:', healthData);
        
        // Test invoices endpoint
        console.log('2. Testing invoices endpoint...');
        const invoicesResponse = await fetch(`${API_URL}/invoices`);
        const invoicesData = await invoicesResponse.json();
        console.log('Invoices response length:', invoicesData.length);
        console.log('First invoice:', invoicesData[0]);
        
        // Test dashboard metrics endpoint
        console.log('3. Testing dashboard metrics endpoint...');
        const metricsResponse = await fetch(`${API_URL}/dashboard/metrics`);
        const metricsData = await metricsResponse.json();
        console.log('Metrics response:', metricsData);
        
        console.log('All API tests passed!');
        return true;
    } catch (error) {
        console.error('API test failed:', error);
        console.error('Error details:', error.message);
        return false;
    }
}

// Run the test
testAPIEndpoints().then(success => {
    if (success) {
        console.log('✅ All API endpoints are working correctly');
    } else {
        console.log('❌ Some API endpoints failed');
    }
});
