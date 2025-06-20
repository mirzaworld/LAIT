// Debug API calls from browser perspective
const API_URL = 'http://localhost:5002/api';

async function debugFrontendAPI() {
    console.log('=== FRONTEND API DEBUG ===');
    
    // Test 1: Check if we can reach the backend
    try {
        console.log('Testing backend health...');
        const healthResponse = await fetch(`${API_URL}/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        console.log('Health Response Status:', healthResponse.status);
        console.log('Health Response Headers:', Object.fromEntries(healthResponse.headers.entries()));
        const healthData = await healthResponse.json();
        console.log('Health Data:', healthData);
    } catch (error) {
        console.error('Health check failed:', error);
    }
    
    // Test 2: Check dashboard metrics
    try {
        console.log('\nTesting dashboard metrics...');
        const metricsResponse = await fetch(`${API_URL}/dashboard/metrics`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        console.log('Metrics Response Status:', metricsResponse.status);
        console.log('Metrics Response Headers:', Object.fromEntries(metricsResponse.headers.entries()));
        
        if (metricsResponse.ok) {
            const metricsData = await metricsResponse.json();
            console.log('Metrics Data:', metricsData);
        } else {
            console.error('Metrics request failed:', metricsResponse.statusText);
        }
    } catch (error) {
        console.error('Metrics API failed:', error);
    }
    
    // Test 3: Check invoices
    try {
        console.log('\nTesting invoices...');
        const invoicesResponse = await fetch(`${API_URL}/invoices`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        console.log('Invoices Response Status:', invoicesResponse.status);
        console.log('Invoices Response Headers:', Object.fromEntries(invoicesResponse.headers.entries()));
        
        if (invoicesResponse.ok) {
            const invoicesData = await invoicesResponse.json();
            console.log('Invoices Count:', invoicesData.length);
            console.log('First Invoice:', invoicesData[0]);
        } else {
            console.error('Invoices request failed:', invoicesResponse.statusText);
        }
    } catch (error) {
        console.error('Invoices API failed:', error);
    }
}

// Run debug when page loads
debugFrontendAPI();
