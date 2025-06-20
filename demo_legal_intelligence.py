#!/usr/bin/env python3
"""
Demo script to showcase LAIT Legal Intelligence features
This script demonstrates the integration with CourtListener API
and shows how the legal spend optimizer can benefit from external legal data.
"""

import requests
import json
import time
from datetime import datetime

def demo_legal_intelligence():
    """
    Demonstrate legal intelligence features
    """
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("LAIT Legal Intelligence Demo")
    print("=" * 60)
    print()
    
    # Test API connectivity
    print("1. Testing API connectivity...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Backend API is running")
            print(f"   Response: {response.json()}")
        else:
            print("❌ Backend API connectivity issues")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    print()
    
    # Test attorney verification (mock data since we don't have real CourtListener API token)
    print("2. Testing Attorney Verification...")
    attorney_data = {
        "attorney_name": "John Smith",
        "law_firm": "Smith & Associates"
    }
    
    try:
        # Note: This will fail without proper JWT token, but demonstrates the endpoint
        response = requests.post(
            f"{base_url}/api/legal-intelligence/verify-attorney",
            json=attorney_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer mock-jwt-token"
            }
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Request failed (expected without proper auth): {e}")
    
    print()
    
    # Test case research
    print("3. Testing Case Research...")
    case_data = {
        "case_description": "Contract dispute involving software licensing terms",
        "court": "Northern District of California"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/legal-intelligence/comprehensive-research",
            json=case_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer mock-jwt-token"
            }
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Request failed (expected without proper auth): {e}")
    
    print()
    
    # Test precedent search
    print("4. Testing Precedent Search...")
    precedent_data = {
        "legal_issue": "Software licensing fair use doctrine",
        "jurisdiction": "ca9"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/legal-intelligence/precedent-research",
            json=precedent_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer mock-jwt-token"
            }
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Request failed (expected without proper auth): {e}")
    
    print()
    
    # Show integration benefits
    print("5. Legal Intelligence Integration Benefits:")
    print("   ✅ Attorney Verification:")
    print("      - Verify credentials before hiring")
    print("      - Check case history and experience")
    print("      - Assess specialization in relevant practice areas")
    print()
    print("   ✅ Case Research:")
    print("      - Find similar cases for cost estimation")
    print("      - Identify case complexity factors")
    print("      - Discover relevant court precedents")
    print()
    print("   ✅ Competitive Intelligence:")
    print("      - Compare law firm performance metrics")
    print("      - Analyze opposing counsel strategies")
    print("      - Benchmark legal spending against market data")
    print()
    print("   ✅ Risk Assessment:")
    print("      - Predict case outcomes based on historical data")
    print("      - Assess judge tendencies and patterns")
    print("      - Calculate risk-adjusted fee estimates")
    print()
    
    # Show data integration workflow
    print("6. Data Integration Workflow:")
    print("   📊 Company Dataset (442k+ legal companies)")
    print("   └── Enhanced vendor database with rich profiles")
    print()
    print("   ⚖️  CourtListener API (legal research)")
    print("   ├── Attorney verification and case history")
    print("   ├── Precedent research and case law analysis")
    print("   ├── Judge information and court analytics")
    print("   └── Competitive intelligence and benchmarking")
    print()
    print("   💡 LAIT Platform Integration")
    print("   ├── Enhanced vendor selection and evaluation")
    print("   ├── Intelligent matter cost estimation")
    print("   ├── Risk-adjusted budget planning")
    print("   └── Data-driven legal spend optimization")
    print()
    
    print("=" * 60)
    print("Demo completed! ")
    print("Frontend available at: http://localhost:5174/legal-intelligence")
    print("Backend API docs: http://localhost:8000/api/")
    print("=" * 60)

if __name__ == "__main__":
    demo_legal_intelligence()
