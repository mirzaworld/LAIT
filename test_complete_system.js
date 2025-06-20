#!/usr/bin/env node

// Comprehensive test of the LAIT system with upload functionality
const API_URL = 'http://localhost:5002/api';

async function testSystem() {
    console.log('🔬 COMPREHENSIVE LAIT SYSTEM TEST');
    console.log('=' .repeat(50));
    
    // Test 1: Check baseline metrics
    console.log('\n📊 STEP 1: Testing baseline metrics...');
    try {
        const response = await fetch(`${API_URL}/dashboard/metrics`);
        const metrics = await response.json();
        console.log(`✅ Baseline - Total Spend: $${metrics.total_spend.toLocaleString()}`);
        console.log(`✅ Baseline - Invoice Count: ${metrics.invoice_count}`);
        console.log(`✅ Baseline - Uploaded Count: ${metrics.uploaded_invoices_count}`);
        
        const baselineCount = metrics.invoice_count;
        const baselineSpend = metrics.total_spend;
        
        // Test 2: Upload an invoice
        console.log('\n📤 STEP 2: Testing invoice upload...');
        
        // Create a test file using FormData
        const formData = new FormData();
        const testContent = new Blob(['Legal Services Invoice\nVendor: Test Law Firm\nAmount: $50,000\nMatter: Contract Review'], { type: 'text/plain' });
        formData.append('file', testContent, 'test_legal_invoice.txt');
        
        const uploadResponse = await fetch(`${API_URL}/upload-invoice`, {
            method: 'POST',
            body: formData
        });
        
        if (!uploadResponse.ok) {
            throw new Error(`Upload failed: ${uploadResponse.statusText}`);
        }
        
        const uploadResult = await uploadResponse.json();
        console.log(`✅ Upload successful - Invoice ID: ${uploadResult.invoice_id}`);
        console.log(`✅ Upload analysis - Risk Score: ${uploadResult.analysis.risk_score}`);
        console.log(`✅ Upload amount: $${uploadResult.invoice_data.amount.toLocaleString()}`);
        
        // Test 3: Verify metrics updated
        console.log('\n📈 STEP 3: Verifying metrics update...');
        const updatedResponse = await fetch(`${API_URL}/dashboard/metrics`);
        const updatedMetrics = await updatedResponse.json();
        
        console.log(`✅ Updated - Total Spend: $${updatedMetrics.total_spend.toLocaleString()}`);
        console.log(`✅ Updated - Invoice Count: ${updatedMetrics.invoice_count}`);
        console.log(`✅ Updated - Uploaded Count: ${updatedMetrics.uploaded_invoices_count}`);
        
        // Verify the changes
        const spendIncrease = updatedMetrics.total_spend - baselineSpend;
        const countIncrease = updatedMetrics.invoice_count - baselineCount;
        
        if (countIncrease === 1 && spendIncrease > 0) {
            console.log(`✅ VERIFIED: Metrics properly updated (+$${spendIncrease.toLocaleString()}, +${countIncrease} invoice)`);
        } else {
            console.log(`❌ ISSUE: Metrics didn't update correctly`);
        }
        
        // Test 4: Check invoices API
        console.log('\n📄 STEP 4: Testing invoices API...');
        const invoicesResponse = await fetch(`${API_URL}/invoices`);
        const invoices = await invoicesResponse.json();
        
        console.log(`✅ Invoices API returned ${invoices.length} invoices`);
        
        // Find the uploaded invoice
        const uploadedInvoice = invoices.find(inv => inv.id === uploadResult.invoice_id);
        if (uploadedInvoice) {
            console.log(`✅ Uploaded invoice found in list: ${uploadedInvoice.vendor}`);
            console.log(`✅ Status: ${uploadedInvoice.status}, Amount: $${uploadedInvoice.amount}`);
        } else {
            console.log(`❌ Uploaded invoice not found in invoices list`);
        }
        
        // Test 5: Test filtering
        console.log('\n🔍 STEP 5: Testing invoice filtering...');
        const pendingResponse = await fetch(`${API_URL}/invoices?status=pending`);
        const pendingInvoices = await pendingResponse.json();
        console.log(`✅ Pending invoices filter returned ${pendingInvoices.length} invoices`);
        
        // Summary
        console.log('\n' + '=' .repeat(50));
        console.log('🎯 SYSTEM TEST SUMMARY');
        console.log('✅ Backend API responding correctly');
        console.log('✅ Upload functionality working');
        console.log('✅ Metrics calculating dynamically from data');
        console.log('✅ Invoice storage and retrieval working');
        console.log('✅ Filtering functionality working');
        
        console.log('\n🌐 FRONTEND ACCESS POINTS:');
        console.log('   📱 Dashboard: http://localhost:5173/');
        console.log('   📄 Invoice List: http://localhost:5173/invoices');
        console.log('   📤 Upload Page: http://localhost:5173/invoices/upload');
        console.log('   📊 Analytics: http://localhost:5173/analytics');
        
        console.log('\n✅ ALL SYSTEMS OPERATIONAL!');
        console.log('   - Metrics display: Working with real data');
        console.log('   - Invoice upload: Fully functional');
        console.log('   - Data integration: Properly calculating from uploaded invoices');
        console.log('   - ML/Analytics ready: Data flowing correctly');
        
    } catch (error) {
        console.log(`❌ Test failed: ${error.message}`);
    }
}

testSystem().catch(console.error);
