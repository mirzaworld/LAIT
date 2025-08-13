#!/usr/bin/env node

const fetch = require('node-fetch');

const API_BASE = 'http://127.0.0.1:5002/api';
const FRONTEND_ORIGIN = 'http://localhost:5174';

async function testEndpoint(endpoint, description) {
    try {
        console.log(`\n🧪 Testing ${description}...`);
        
        // Test OPTIONS preflight request first
        const optionsResponse = await fetch(`${API_BASE}${endpoint}`, {
            method: 'OPTIONS',
            headers: {
                'Origin': FRONTEND_ORIGIN,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        });
        
        console.log(`   OPTIONS ${endpoint}: ${optionsResponse.status} ${optionsResponse.statusText}`);
        console.log(`   CORS Headers: ${optionsResponse.headers.get('Access-Control-Allow-Origin')}`);
        
        // Test actual GET request
        const getResponse = await fetch(`${API_BASE}${endpoint}`, {
            method: 'GET',
            headers: {
                'Origin': FRONTEND_ORIGIN,
                'Content-Type': 'application/json'
            }
        });
        
        console.log(`   GET ${endpoint}: ${getResponse.status} ${getResponse.statusText}`);
        
        if (getResponse.ok) {
            const data = await getResponse.json();
            console.log(`   ✅ Data received:`, JSON.stringify(data, null, 2).substring(0, 200) + '...');
        } else {
            console.log(`   ❌ Error: ${getResponse.statusText}`);
        }
        
        return getResponse.ok;
        
    } catch (error) {
        console.log(`   ❌ Network Error: ${error.message}`);
        return false;
    }
}

async function runTests() {
    console.log('🚀 LAIT Frontend-Backend Integration Test');
    console.log(`Backend: ${API_BASE}`);
    console.log(`Frontend Origin: ${FRONTEND_ORIGIN}`);
    console.log('='.repeat(60));
    
    const tests = [
        ['/health', 'Health Check'],
        ['/invoices', 'Invoice List'],
        ['/dashboard/metrics', 'Dashboard Metrics']
    ];
    
    let passed = 0;
    let total = tests.length;
    
    for (const [endpoint, description] of tests) {
        if (await testEndpoint(endpoint, description)) {
            passed++;
        }
    }
    
    console.log('\n' + '='.repeat(60));
    console.log(`📊 Test Results: ${passed}/${total} endpoints working`);
    
    if (passed === total) {
        console.log('🎉 All tests PASSED! Frontend should work without CORS errors.');
    } else {
        console.log('❌ Some tests FAILED. Check the output above for details.');
    }
}

runTests().catch(console.error);
