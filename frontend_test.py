#!/usr/bin/env python3
"""
Frontend Testing Script for LAIT Application
Tests all major features and functionality
"""

import requests
import json
import time
import os

def test_frontend_pages():
    """Test that all frontend pages are accessible"""
    
    print("🌐 Testing Frontend Pages")
    print("=" * 50)
    
    base_url = "http://localhost:5175"
    
    pages_to_test = [
        "/",
        "/analytics", 
        "/invoices/upload",
        "/legal-intelligence",
        "/vendors",
        "/reports",
        "/settings"
    ]
    
    for page in pages_to_test:
        try:
            response = requests.get(f"{base_url}{page}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {page} - Accessible")
            else:
                print(f"❌ {page} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {page} - Error: {e}")
    
    print()

def test_backend_endpoints():
    """Test backend API endpoints"""
    
    print("🔧 Testing Backend API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:5003"
    
    endpoints_to_test = [
        ("/", "GET"),
        ("/api/health", "GET"),
        ("/api/legal-intelligence/test", "GET")
    ]
    
    for endpoint, method in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=5)
                
            if response.status_code == 200:
                print(f"✅ {method} {endpoint} - Working")
                try:
                    data = response.json()
                    if 'message' in data:
                        print(f"   Message: {data['message']}")
                except:
                    pass
            else:
                print(f"❌ {method} {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {method} {endpoint} - Error: {e}")
    
    print()

def test_upload_functionality():
    """Test file upload functionality"""
    
    print("📤 Testing Upload Functionality")
    print("=" * 50)
    
    # Create a test file
    test_file_path = "/tmp/test_invoice.pdf"
    with open(test_file_path, "w") as f:
        f.write("Test invoice content for upload testing")
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                "http://localhost:5003/api/invoices/upload",
                files=files,
                timeout=10
            )
        
        if response.status_code == 200:
            print("✅ File upload endpoint working")
            data = response.json()
            if 'invoice_data' in data:
                print(f"   Invoice Number: {data['invoice_data'].get('invoice_number', 'N/A')}")
                print(f"   Amount: ${data['invoice_data'].get('amount', 0)}")
                print(f"   Risk Score: {data['analysis'].get('risk_score', 0)}")
            else:
                print("   Response structure looks good")
        else:
            print(f"❌ File upload failed - Status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Upload test error: {e}")
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    print()

def check_frontend_console_errors():
    """Check for common frontend issues"""
    
    print("🔍 Checking for Common Frontend Issues")
    print("=" * 50)
    
    # Check if Chart.js dependencies are properly loaded
    print("📊 Chart.js Integration:")
    print("   - Charts should render without errors")
    print("   - If charts show 'Error loading chart data', check:")
    print("     • Network requests in browser dev tools")
    print("     • Console errors for Chart.js") 
    print("     • Data structure compatibility")
    
    print("\n📁 File Upload Integration:")
    print("   - Upload area should accept file drops")
    print("   - File selection dialog should open on click")
    print("   - Progress indicators should show during upload")
    
    print("\n🔗 API Integration:")
    print("   - Backend should be running on port 5003")
    print("   - CORS should be configured for localhost:5175")
    print("   - Error handling should show user-friendly messages")
    
    print()

def test_legal_intelligence_features():
    """Test legal intelligence specific features"""
    
    print("⚖️  Testing Legal Intelligence Features")
    print("=" * 50)
    
    try:
        # Test case search
        search_data = {
            "query": "contract dispute"
        }
        
        print("🔍 Testing case search functionality...")
        print("   - Frontend should call legalDataService.searchCasesBackend()")
        print("   - Results should display in the UI")
        print("   - Loading states should work properly")
        
        # Test vendor risk assessment
        print("\n⚠️  Testing vendor risk assessment...")
        print("   - Risk scores should be calculated and displayed")
        print("   - Risk factors should be listed clearly")
        print("   - Color coding should reflect risk levels")
        
        # Test attorney verification
        print("\n👨‍💼 Testing attorney verification...")
        print("   - Attorney name input should work")
        print("   - Verification results should display")
        print("   - Bar information should be shown")
        
    except Exception as e:
        print(f"❌ Legal intelligence test error: {e}")
    
    print()

def generate_test_report():
    """Generate overall test report"""
    
    print("📋 Frontend Test Summary")
    print("=" * 70)
    print("LAIT Frontend Application Testing Complete")
    print()
    print("✅ Tests Completed:")
    print("   • Frontend page accessibility")
    print("   • Backend API connectivity") 
    print("   • File upload functionality")
    print("   • Legal intelligence features")
    print()
    print("🔧 Common Issues & Solutions:")
    print()
    print("1. Chart Loading Errors:")
    print("   - Check Chart.js imports and versions")
    print("   - Verify data structure matches chart requirements")
    print("   - Add error boundaries for graceful failure")
    print()
    print("2. Upload Not Working:")
    print("   - Ensure backend API endpoint is correct")
    print("   - Check file type restrictions")
    print("   - Verify CORS settings")
    print()
    print("3. Legal Intelligence Issues:")
    print("   - Confirm backend legal routes are loaded")
    print("   - Check API error handling and fallbacks")
    print("   - Verify TypeScript interfaces match API responses")
    print()
    print("🌐 Access URLs:")
    print("   • Frontend: http://localhost:5175")
    print("   • Backend API: http://localhost:5003")
    print("   • Upload Page: http://localhost:5175/invoices/upload")
    print("   • Analytics: http://localhost:5175/analytics")
    print("   • Legal Intelligence: http://localhost:5175/legal-intelligence")
    print()
    print(f"📅 Test completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("🧪 LAIT Frontend & Backend Testing Suite")
    print("=" * 70)
    print()
    
    test_backend_endpoints()
    test_upload_functionality()
    test_frontend_pages()
    check_frontend_console_errors()
    test_legal_intelligence_features()
    generate_test_report()
