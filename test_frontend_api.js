#!/usr/bin/env node

// Simple test script to validate frontend API communication
const API_URL = 'http://localhost:5002/api';

async function testEndpoint(endpoint, description) {
    try {
        console.log(`\n🔍 Testing ${description}...`);
        console.log(`   URL: ${API_URL}${endpoint}`);
        
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Origin': 'http://localhost:5173'
            }
        });
        
        console.log(`   Status: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`   ✅ Success! Received ${JSON.stringify(data).length} characters of data`);
        
        if (endpoint === '/dashboard/metrics') {
            console.log(`   📊 Metrics summary:`);
            console.log(`      - Total Spend: $${data.total_spend?.toLocaleString() || 'N/A'}`);
            console.log(`      - Invoice Count: ${data.invoice_count || 'N/A'}`);
            console.log(`      - Risk Factors: ${data.risk_factors_count || 'N/A'}`);
        } else if (endpoint === '/invoices') {
            console.log(`   📋 Invoices summary:`);
            console.log(`      - Invoice count: ${data.length || 'N/A'}`);
            if (data.length > 0) {
                console.log(`      - First invoice: ${data[0].vendor} - $${data[0].amount}`);
            }
        }
        
        return true;
    } catch (error) {
        console.log(`   ❌ Failed: ${error.message}`);
        return false;
    }
}

async function runTests() {
    console.log('🚀 Starting Frontend API Tests...');
    console.log('=' .repeat(50));
    
    const tests = [
        ['/health', 'Health Check'],
        ['/dashboard/metrics', 'Dashboard Metrics'],
        ['/invoices', 'Invoices List'],
        ['/vendors', 'Vendors List']
    ];
    
    let passed = 0;
    let total = tests.length;
    
    for (const [endpoint, description] of tests) {
        const success = await testEndpoint(endpoint, description);
        if (success) passed++;
    }
    
    console.log('\n' + '=' .repeat(50));
    console.log(`🎯 Results: ${passed}/${total} tests passed`);
    
    if (passed === total) {
        console.log('🎉 All tests passed! Frontend should be able to communicate with backend.');
    } else {
        console.log('⚠️  Some tests failed. Check the backend server and endpoints.');
    }
}

// Run the tests
runTests().catch(console.error);
