// Debug script to test the frontend API calls and identify issues
console.log('=== LAIT Frontend API Debug ===');

async function testFrontendAPI() {
    const BASE_URL = 'http://localhost:5003';
    
    console.log('1. Testing API health...');
    try {
        const healthResponse = await fetch(`${BASE_URL}/api/health`);
        const healthData = await healthResponse.json();
        console.log('✅ Health check:', healthData);
    } catch (error) {
        console.error('❌ Health check failed:', error);
    }
    
    console.log('\n2. Testing dashboard metrics...');
    try {
        const metricsResponse = await fetch(`${BASE_URL}/api/dashboard/metrics`);
        const metricsData = await metricsResponse.json();
        console.log('✅ Dashboard metrics:', metricsData);
    } catch (error) {
        console.error('❌ Dashboard metrics failed:', error);
    }
    
    console.log('\n3. Testing invoices endpoint...');
    try {
        const invoicesResponse = await fetch(`${BASE_URL}/api/invoices`);
        const invoicesData = await invoicesResponse.json();
        console.log('✅ Invoices:', invoicesData);
    } catch (error) {
        console.error('❌ Invoices failed:', error);
    }
    
    console.log('\n4. Testing vendors endpoint...');
    try {
        const vendorsResponse = await fetch(`${BASE_URL}/api/vendors`);
        const vendorsData = await vendorsResponse.json();
        console.log('✅ Vendors:', vendorsData);
    } catch (error) {
        console.error('❌ Vendors failed:', error);
    }
    
    console.log('\n5. Testing spend trends...');
    try {
        const trendsResponse = await fetch(`${BASE_URL}/api/spend-trends`);
        const trendsData = await trendsResponse.json();
        console.log('✅ Spend trends:', trendsData);
    } catch (error) {
        console.error('❌ Spend trends failed:', error);
    }
    
    console.log('\n6. Testing file upload capability...');
    const formData = new FormData();
    formData.append('file', new Blob(['test invoice content'], { type: 'text/plain' }), 'test-invoice.txt');
    formData.append('vendor', 'Test Vendor');
    formData.append('amount', '1000');
    formData.append('date', '2024-01-15');
    formData.append('category', 'Legal Services');
    formData.append('description', 'Test invoice for debug');
    
    try {
        const uploadResponse = await fetch(`${BASE_URL}/api/upload-invoice`, {
            method: 'POST',
            body: formData
        });
        const uploadData = await uploadResponse.json();
        console.log('✅ Upload test:', uploadData);
    } catch (error) {
        console.error('❌ Upload test failed:', error);
    }
    
    console.log('\n=== Debug Complete ===');
}

// Run the test
testFrontendAPI();
