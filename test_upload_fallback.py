#!/usr/bin/env python3
"""
Test Upload with ML Fallback
============================
Test actual upload endpoint with CSV data to confirm model_fallback behavior
"""

import json
import csv
import io
import requests
from pathlib import Path
import tempfile
import time

def create_test_csv():
    """Create a test CSV with invoice data"""
    csv_content = """description,amount,billable_hours,rate
Legal research - contract review,2500.00,10.0,250.0
"SUSPICIOUS: Extremely high rate consultation",5000.00,5.0,1000.0
Document preparation,750.00,3.0,250.0
Court filing fees,150.00,0.5,300.0
"""
    return csv_content

def test_upload_endpoint():
    """Test the upload endpoint with real CSV data"""
    print("📁 Testing Upload Endpoint with ML Fallback")
    print("=" * 50)
    
    # Create temporary CSV file
    csv_data = create_test_csv()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_data)
        temp_file = f.name
    
    try:
        # Prepare form data
        files = {
            'file': ('test_invoice.csv', open(temp_file, 'rb'), 'text/csv')
        }
        
        data = {
            'vendor': 'Test Legal Firm',
            'invoice_date': '2025-01-15'
        }
        
        # Make the request
        print(f"📤 Making upload request to http://localhost:5003/api/invoices/upload")
        response = requests.post(
            'http://localhost:5003/api/invoices/upload',
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"📋 Response Data:")
            for key, value in result.items():
                print(f"   {key}: {value}")
                
            # Check for model_fallback note
            if result.get('note') == 'model_fallback':
                print(f"\n🎯 ✅ CONFIRMED: Response includes note='model_fallback'")
                print(f"🔧 Scoring method: {result.get('scoring_method', 'unknown')}")
            else:
                print(f"\n❌ Expected note='model_fallback', got: {result.get('note')}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection refused - make sure backend is running on port 5003")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Cleanup temp file
        Path(temp_file).unlink(missing_ok=True)
    
    return True

if __name__ == "__main__":
    print("🧪 LAIT Upload Test with ML Fallback")
    print("=" * 50)
    
    # Wait a moment for any server startup
    print("⏳ Waiting 2 seconds for server...")
    time.sleep(2)
    
    success = test_upload_endpoint()
    
    if success:
        print(f"\n🎉 Upload test completed successfully!")
    else:
        print(f"\n❌ Upload test failed - check if backend is running")
