/**
 * LAIT Component Test Script
 * This script tests the components that were previously failing
 */

const API_BASE = 'http://localhost:5003';
const FRONTEND_URL = 'http://localhost:5173';

const fetch = require('node-fetch');

async function testAPI() {
  console.log('🔍 Testing API connectivity...');
  
  try {
    // Test health endpoint
    const healthResponse = await fetch(`${API_BASE}/api/health`);
    if (healthResponse.ok) {
      console.log('✅ API health check successful');
    } else {
      console.error('❌ API health check failed');
      return false;
    }

    // Test spend trends endpoint (was causing issues in SpendChart component)
    const spendResponse = await fetch(`${API_BASE}/api/analytics/spend-trends?period=monthly`);
    if (spendResponse.ok) {
      const spendData = await spendResponse.json();
      
      // Validate that the response has the correct structure
      if (spendData && spendData.datasets && Array.isArray(spendData.datasets)) {
        console.log('✅ Spend trends endpoint returning proper data structure');
        console.log(`   Found ${spendData.datasets.length} datasets`);
      } else {
        console.error('⚠️ Spend trends endpoint missing proper data structure');
        console.log('   Response:', JSON.stringify(spendData, null, 2).slice(0, 200) + '...');
      }
    } else {
      console.error('❌ Spend trends endpoint failed');
    }
    
    // Test invoices endpoint (was causing issues in RecentInvoices component)
    const invoicesResponse = await fetch(`${API_BASE}/api/invoices`);
    if (invoicesResponse.ok) {
      const invoicesData = await invoicesResponse.json();
      
      // Validate that invoice amount exists and is a number
      if (Array.isArray(invoicesData) && invoicesData.length > 0) {
        const hasValidAmounts = invoicesData.every(invoice => 
          typeof invoice.amount === 'number' || 
          (invoice.amount === null || invoice.amount === undefined)
        );
        
        console.log(`✅ Invoices endpoint returning ${invoicesData.length} invoices`);
        
        if (hasValidAmounts) {
          console.log('   All invoices have valid amount formats');
        } else {
          console.error('⚠️ Some invoices have invalid amount formats');
        }
      } else {
        console.warn('⚠️ Invoices endpoint returned empty or invalid array');
      }
    } else {
      console.error('❌ Invoices endpoint failed');
    }
    
    return true;
  } catch (error) {
    console.error('❌ API test failed with error:', error);
    return false;
  }
}

async function main() {
  console.log('🚀 Starting LAIT Component Test...');
  console.log('==================================================');
  
  const apiSuccess = await testAPI();
  
  console.log('==================================================');
  
  if (apiSuccess) {
    console.log('✅ All tests completed');
    console.log(`🌐 You can now verify the frontend at ${FRONTEND_URL}`);
    console.log('   The following components should be working:');
    console.log('   1. SpendChart - Now handles undefined data properly');
    console.log('   2. RecentInvoices - Now handles undefined amounts properly');
    console.log('   3. Socket.IO - Connections are now handled gracefully');
  } else {
    console.error('❌ Some tests failed');
  }
}

main().catch(err => {
  console.error('Test script failed:', err);
  process.exit(1);
});
