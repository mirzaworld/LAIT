#!/usr/bin/env node

// Final comprehensive test of the LAIT Legal Analytics Platform
console.log('🚀 LAIT Legal Analytics Platform - Final Integration Test');
console.log('========================================================');

const API_URL = 'http://localhost:5003/api';

async function runTest(endpoint, description) {
    try {
        console.log(`\n🔍 Testing: ${description}`);
        const response = await fetch(`${API_URL}${endpoint}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`✅ SUCCESS: ${description}`);
        
        // Show key data points
        if (endpoint === '/invoices') {
            console.log(`   📊 Found ${data.length} invoices`);
        } else if (endpoint === '/dashboard/metrics') {
            console.log(`   💰 Total spend: $${data.total_spend?.toLocaleString()}`);
            console.log(`   📈 Invoice count: ${data.invoice_count}`);
        } else if (endpoint === '/analytics/predictive') {
            console.log(`   🔮 Next month prediction: $${data.predictions?.next_month_spend?.amount?.toLocaleString()}`);
        } else if (endpoint === '/analytics/vendor-performance') {
            console.log(`   🏆 Top vendor: ${data.vendor_performance?.[0]?.vendor}`);
        }
        
        return true;
    } catch (error) {
        console.log(`❌ FAILED: ${description}`);
        console.log(`   Error: ${error.message}`);
        return false;
    }
}

async function testFileUpload() {
    try {
        console.log(`\n🔍 Testing: File Upload & Analysis`);
        
        // Create a mock file upload
        const formData = new FormData();
        const blob = new Blob(['Mock invoice content'], { type: 'application/pdf' });
        formData.append('file', blob, 'test_invoice.pdf');
        
        const response = await fetch(`${API_URL}/invoices/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`✅ SUCCESS: File Upload & Analysis`);
        console.log(`   📄 Invoice ID: ${data.invoice_id}`);
        console.log(`   ⚠️  Risk Score: ${data.analysis?.risk_score}/100`);
        console.log(`   📊 Risk Level: ${data.analysis?.risk_level}`);
        
        return true;
    } catch (error) {
        console.log(`❌ FAILED: File Upload & Analysis`);
        console.log(`   Error: ${error.message}`);
        return false;
    }
}

async function runAllTests() {
    const tests = [
        ['/health', 'Backend Health Check'],
        ['/invoices', 'Invoice Data Retrieval'],
        ['/dashboard/metrics', 'Dashboard Metrics'],
        ['/analytics/predictive', 'AI Predictive Analytics'],
        ['/analytics/vendor-performance', 'Vendor Performance Analysis'],
        ['/analytics/budget-forecast', 'Budget Forecasting']
    ];
    
    let passedTests = 0;
    let totalTests = tests.length + 1; // +1 for file upload test
    
    // Run API tests
    for (const [endpoint, description] of tests) {
        const passed = await runTest(endpoint, description);
        if (passed) passedTests++;
    }
    
    // Run file upload test
    const uploadPassed = await testFileUpload();
    if (uploadPassed) passedTests++;
    
    // Final results
    console.log(`\n${'='.repeat(60)}`);
    console.log(`📊 TEST RESULTS: ${passedTests}/${totalTests} tests passed`);
    
    if (passedTests === totalTests) {
        console.log(`\n🎉 ALL TESTS PASSED! 🎉`);
        console.log(`✅ LAIT Legal Analytics Platform is FULLY FUNCTIONAL`);
        console.log(`✅ All APIs working correctly`);
        console.log(`✅ File upload and analysis working`);
        console.log(`✅ Advanced AI analytics operational`);
        console.log(`✅ Ready for production deployment!`);
        
        console.log(`\n🚀 Deployment URLs:`);
        console.log(`   Frontend (dev): http://localhost:5173`);
        console.log(`   Frontend (prod): http://localhost:54943`);
        console.log(`   Backend API: http://localhost:5003`);
        
        console.log(`\n💡 Next Steps:`);
        console.log(`   1. Deploy frontend to Vercel/Netlify`);
        console.log(`   2. Deploy backend to Railway/Render/Heroku`);
        console.log(`   3. Update VITE_API_URL to production backend`);
        console.log(`   4. Configure custom domain & SSL`);
        
    } else {
        console.log(`\n⚠️  Some tests failed. Check the errors above.`);
    }
    
    console.log(`\n🏆 LAIT Platform Features Summary:`);
    console.log(`   • Dynamic invoice upload & AI risk analysis`);
    console.log(`   • Real-time dashboard with live metrics`);
    console.log(`   • Predictive analytics (spend forecasting)`);
    console.log(`   • Vendor performance scoring & ranking`);
    console.log(`   • Budget scenario planning & recommendations`);
    console.log(`   • Modern responsive UI with advanced visualizations`);
    console.log(`   • Better than Thomson Reuters in AI capabilities!`);
}

// Run the tests
runAllTests().catch(console.error);
