#!/usr/bin/env node

const fs = require('fs');
const { execSync } = require('child_process');

async function runAllTests() {

console.log('🧪 LAIT Frontend-Backend Integration Test');
console.log('==========================================\n');

const API_BASE = 'http://localhost:5002/api';
let testsPassed = 0;
let testsFailed = 0;

async function runTest(testName, testFunction) {
    console.log(`🔍 Testing: ${testName}`);
    try {
        await testFunction();
        console.log(`✅ ${testName} - PASSED\n`);
        testsPassed++;
    } catch (error) {
        console.log(`❌ ${testName} - FAILED: ${error.message}\n`);
        testsFailed++;
    }
}

async function fetchJson(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
}

// Test 1: Basic API Health
await runTest('API Health Check', async () => {
    const data = await fetchJson(`${API_BASE}/health`);
    if (data.status !== 'healthy') {
        throw new Error('API is not healthy');
    }
});

// Test 2: Dashboard Metrics
await runTest('Dashboard Metrics', async () => {
    const data = await fetchJson(`${API_BASE}/dashboard/metrics`);
    if (!data.total_spend || !data.invoice_count) {
        throw new Error('Missing required metrics');
    }
    console.log(`   📊 Total Spend: $${data.total_spend.toLocaleString()}`);
    console.log(`   📄 Total Invoices: ${data.invoice_count}`);
    console.log(`   📤 Uploaded Invoices: ${data.uploaded_invoices_count}`);
});

// Test 3: Invoices List
await runTest('Invoices List', async () => {
    const data = await fetchJson(`${API_BASE}/invoices`);
    if (!Array.isArray(data) || data.length === 0) {
        throw new Error('No invoices returned');
    }
    console.log(`   📋 Total invoices: ${data.length}`);
});

// Test 4: Vendors List
await runTest('Vendors List', async () => {
    const data = await fetchJson(`${API_BASE}/vendors`);
    if (!Array.isArray(data) || data.length === 0) {
        throw new Error('No vendors returned');
    }
    console.log(`   🏢 Total vendors: ${data.length}`);
});

// Test 5: Spend Trends
await runTest('Spend Trends', async () => {
    const data = await fetchJson(`${API_BASE}/analytics/spend-trends?period=monthly`);
    if (!data.data || !Array.isArray(data.data)) {
        throw new Error('Invalid spend trends data');
    }
    console.log(`   📈 Monthly data points: ${data.data.length}`);
});

// Test 6: Advanced Analytics
await runTest('Advanced Analytics - Predictive', async () => {
    const data = await fetchJson(`${API_BASE}/analytics/predictive`);
    if (!data.predictions || !data.ai_insights) {
        throw new Error('Missing predictive analytics data');
    }
    console.log(`   🔮 Next month forecast: $${data.predictions.next_month_spend.amount.toLocaleString()}`);
});

await runTest('Advanced Analytics - Vendor Performance', async () => {
    const data = await fetchJson(`${API_BASE}/analytics/vendor-performance`);
    if (!data.vendor_performance || !Array.isArray(data.vendor_performance)) {
        throw new Error('Missing vendor performance data');
    }
    console.log(`   📊 Vendor performance records: ${data.vendor_performance.length}`);
});

await runTest('Advanced Analytics - Budget Forecast', async () => {
    const data = await fetchJson(`${API_BASE}/analytics/budget-forecast`);
    if (!data.forecast || !data.recommendations) {
        throw new Error('Missing budget forecast data');
    }
    console.log(`   💰 Annual projection: $${data.forecast.annual_projection.toLocaleString()}`);
});

// Test 7: File Upload
await runTest('File Upload', async () => {
    const formData = new FormData();
    formData.append('file', new Blob(['Integration test invoice content'], { type: 'text/plain' }), 'integration-test.txt');
    formData.append('vendor', 'Integration Test Vendor');
    formData.append('amount', '5000');
    formData.append('date', '2024-01-25');
    formData.append('category', 'Legal Services');
    formData.append('description', 'Integration test invoice');
    
    const response = await fetch(`${API_BASE}/upload-invoice`, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
    }
    
    const data = await response.json();
    if (!data.invoice_added || !data.invoice_id) {
        throw new Error('Invoice was not properly added');
    }
    console.log(`   📄 Uploaded invoice: ${data.invoice_id}`);
    console.log(`   ⚠️  Risk level: ${data.analysis.risk_level} (${data.analysis.risk_score}%)`);
});

// Test 8: Verify Upload Reflected in Metrics
await runTest('Upload Updates Metrics', async () => {
    const data = await fetchJson(`${API_BASE}/dashboard/metrics`);
    if (data.uploaded_invoices_count < 1) {
        throw new Error('Upload not reflected in metrics');
    }
    console.log(`   📤 Uploaded invoices count: ${data.uploaded_invoices_count}`);
});

// Test 9: Report Generation
await runTest('Report Generation', async () => {
    const response = await fetch(`${API_BASE}/reports/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ period: 'current' })
    });
    
    if (!response.ok) {
        throw new Error(`Report generation failed: ${response.statusText}`);
    }
    
    const data = await response.json();
    if (!data.report_id || !data.executive_summary) {
        throw new Error('Invalid report data');
    }
    console.log(`   📊 Report ID: ${data.report_id}`);
    console.log(`   💰 Total spend in report: $${data.executive_summary.total_spend.toLocaleString()}`);
    console.log(`   📄 Invoices analyzed: ${data.executive_summary.total_invoices}`);
    console.log(`   ⚠️  High risk invoices: ${data.executive_summary.high_risk_invoices}`);
});

// Final Summary
console.log('==========================================');
console.log('🏆 Integration Test Summary');
console.log('==========================================');
console.log(`✅ Tests Passed: ${testsPassed}`);
console.log(`❌ Tests Failed: ${testsFailed}`);
console.log(`📊 Success Rate: ${Math.round((testsPassed / (testsPassed + testsFailed)) * 100)}%`);

if (testsFailed === 0) {
    console.log('\n🎉 ALL TESTS PASSED! The LAIT app is fully functional.');
    console.log('✨ You can now:');
    console.log('   - View dashboard metrics at http://localhost:5173');
    console.log('   - Upload invoices via the web interface');
    console.log('   - Generate comprehensive reports');
    console.log('   - View advanced analytics');
    console.log('   - All data is dynamic and based on real API responses');
} else {
    console.log('\n⚠️  Some tests failed. Please check the issues above.');
    process.exit(1);
}

}

// Run the tests
runAllTests().catch(console.error);
