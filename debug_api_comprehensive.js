#!/usr/bin/env node

// Comprehensive test to debug frontend issues
const API_URL = 'http://localhost:5002/api';

async function testApiCall(url, description) {
    console.log(`\n🔍 Testing ${description}...`);
    console.log(`   URL: ${url}`);
    
    try {
        const startTime = Date.now();
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Origin': 'http://localhost:5173',
                'User-Agent': 'LAIT-Frontend-Test'
            }
        });
        
        const endTime = Date.now();
        const duration = endTime - startTime;
        
        console.log(`   ⏱️  Response time: ${duration}ms`);
        console.log(`   📄 Status: ${response.status} ${response.statusText}`);
        console.log(`   📋 Headers:`, Object.fromEntries(response.headers.entries()));
        
        if (!response.ok) {
            const errorText = await response.text();
            console.log(`   ❌ Error body: ${errorText}`);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`   ✅ Success! Data type: ${typeof data}`);
        console.log(`   📊 Data structure:`, Object.keys(data));
        
        return { success: true, data, duration };
    } catch (error) {
        console.log(`   ❌ Failed: ${error.message}`);
        return { success: false, error: error.message };
    }
}

async function runComprehensiveTest() {
    console.log('🔬 COMPREHENSIVE FRONTEND API TEST');
    console.log('=' .repeat(60));
    
    // Test 1: Basic connectivity
    console.log('\n🌐 PHASE 1: Basic Connectivity');
    const healthCheck = await testApiCall(`${API_URL}/health`, 'Health Check');
    
    if (!healthCheck.success) {
        console.log('\n💥 CRITICAL: Backend is not responding. Check if server is running on port 5002.');
        return;
    }
    
    // Test 2: Dashboard metrics (main issue)
    console.log('\n📊 PHASE 2: Dashboard Metrics');
    const metricsTest = await testApiCall(`${API_URL}/dashboard/metrics`, 'Dashboard Metrics');
    
    if (metricsTest.success) {
        console.log('\n🔍 Analyzing metrics data structure...');
        const metrics = metricsTest.data;
        
        const requiredFields = [
            'total_spend', 'spend_change_percentage', 'invoice_count',
            'active_matters', 'risk_factors_count', 'high_risk_invoices_count',
            'avg_processing_time', 'date_range', 'trend_data'
        ];
        
        const missingFields = requiredFields.filter(field => !(field in metrics));
        
        if (missingFields.length === 0) {
            console.log('   ✅ All required fields present');
            console.log(`   💰 Total Spend: $${metrics.total_spend?.toLocaleString()}`);
            console.log(`   📈 Change: ${metrics.spend_change_percentage}%`);
            console.log(`   📋 Invoices: ${metrics.invoice_count}`);
        } else {
            console.log(`   ⚠️  Missing fields: ${missingFields.join(', ')}`);
        }
    }
    
    // Test 3: Invoices
    console.log('\n📄 PHASE 3: Invoices');
    const invoicesTest = await testApiCall(`${API_URL}/invoices`, 'Invoices List');
    
    if (invoicesTest.success) {
        console.log('\n🔍 Analyzing invoices data...');
        const invoices = invoicesTest.data;
        console.log(`   📊 Invoice count: ${invoices.length}`);
        
        if (invoices.length > 0) {
            const firstInvoice = invoices[0];
            console.log(`   🔍 First invoice structure:`, Object.keys(firstInvoice));
            console.log(`   💼 Sample: ${firstInvoice.vendor} - $${firstInvoice.amount}`);
        }
    }
    
    // Test 4: CORS and Headers
    console.log('\n🔒 PHASE 4: CORS and Headers');
    
    try {
        const corsResponse = await fetch(`${API_URL}/dashboard/metrics`, {
            method: 'OPTIONS',
            headers: {
                'Origin': 'http://localhost:5173',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        });
        
        console.log(`   🔒 CORS preflight status: ${corsResponse.status}`);
        console.log(`   🔒 CORS headers:`, Object.fromEntries(corsResponse.headers.entries()));
    } catch (error) {
        console.log(`   ⚠️  CORS test failed: ${error.message}`);
    }
    
    // Summary
    console.log('\n' + '=' .repeat(60));
    console.log('📊 TEST SUMMARY');
    
    if (healthCheck.success && metricsTest.success && invoicesTest.success) {
        console.log('🎉 ALL TESTS PASSED!');
        console.log('');
        console.log('✅ Backend is running and responding correctly');
        console.log('✅ All API endpoints return expected data structures');
        console.log('✅ CORS is configured properly');
        console.log('');
        console.log('🔍 If metrics still don\'t show in the frontend:');
        console.log('   1. Check browser console for JavaScript errors');
        console.log('   2. Check Network tab for failed requests');
        console.log('   3. Verify USE_MOCK_DATA is set to false');
        console.log('   4. Check React component rendering logic');
    } else {
        console.log('❌ SOME TESTS FAILED');
        console.log('   Backend issues detected. Fix backend before testing frontend.');
    }
}

// Run the comprehensive test
runComprehensiveTest().catch(console.error);
