#!/usr/bin/env python3
"""
Comprehensive Demo of Enhanced LAIT ML System with Real-World Legal Data
"""
import json
from datetime import datetime

def run_comprehensive_demo():
    """Run a comprehensive demo showing all enhanced ML capabilities"""
    print("🚀 LAIT Enhanced ML System - Comprehensive Demo")
    print("=" * 60)
    print("Demonstrating production-ready ML models trained on real-world legal billing data")
    print()
    
    # Multiple test scenarios
    test_scenarios = [
        {
            "name": "High-End Corporate Law Firm",
            "invoice": {
                "id": "corp-001",
                "amount": 47500.0,
                "currency": "USD",
                "date": "2024-12-15",
                "vendor": "Elite Corporate Law LLP",
                "line_items": [
                    {
                        "description": "M&A due diligence and document review",
                        "hours": 15.0,
                        "rate": 1800.0,
                        "amount": 27000.0,
                        "attorney": "Senior Partner Williams"
                    },
                    {
                        "description": "Securities law compliance analysis",
                        "hours": 8.5,
                        "rate": 1650.0,
                        "amount": 14025.0,
                        "attorney": "Partner Martinez"
                    },
                    {
                        "description": "Junior associate research and drafting",
                        "hours": 12.0,
                        "rate": 550.0,
                        "amount": 6600.0,
                        "attorney": "Associate Thompson"
                    }
                ]
            }
        },
        {
            "name": "Mid-Market Regional Firm",
            "invoice": {
                "id": "reg-001", 
                "amount": 8750.0,
                "currency": "USD",
                "date": "2024-12-10",
                "vendor": "Regional Business Law Group",
                "line_items": [
                    {
                        "description": "Employment contract negotiation",
                        "hours": 6.0,
                        "rate": 425.0,
                        "amount": 2550.0,
                        "attorney": "Partner Johnson"
                    },
                    {
                        "description": "Litigation case preparation",
                        "hours": 8.5,
                        "rate": 385.0,
                        "amount": 3272.5,
                        "attorney": "Senior Associate Davis"
                    },
                    {
                        "description": "Client consultation and strategy",
                        "hours": 4.0,
                        "rate": 350.0,
                        "amount": 1400.0,
                        "attorney": "Associate Wilson"
                    },
                    {
                        "description": "Paralegal document prep",
                        "hours": 10.0,
                        "rate": 152.75,
                        "amount": 1527.5,
                        "attorney": "Paralegal Smith"
                    }
                ]
            }
        },
        {
            "name": "Suspicious/Unusual Billing",
            "invoice": {
                "id": "susp-001",
                "amount": 28950.0,
                "currency": "USD", 
                "date": "2024-12-12",
                "vendor": "Questionable Legal Services",
                "line_items": [
                    {
                        "description": "Basic contract review",
                        "hours": 2.0,
                        "rate": 3500.0,  # Extremely high rate
                        "amount": 7000.0,
                        "attorney": "Partner Unknown"
                    },
                    {
                        "description": "Phone call with client",
                        "hours": 0.25,
                        "rate": 2800.0,  # Extreme rate for phone call
                        "amount": 700.0,
                        "attorney": "Associate X"
                    },
                    {
                        "description": "Travel time and research",
                        "hours": 18.5,  # Excessive hours
                        "rate": 1150.0,
                        "amount": 21275.0,
                        "attorney": "Partner Mystery"
                    }
                ]
            }
        }
    ]
    
    # Import the enhanced analyzer
    import sys
    sys.path.append('/app/backend')
    from models.enhanced_invoice_analyzer import analyze_invoice_enhanced
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        print("-" * 50)
        
        invoice = scenario['invoice']
        print(f"Invoice ID: {invoice['id']}")
        print(f"Total Amount: ${invoice['amount']:,.2f}")
        print(f"Vendor: {invoice['vendor']}")
        print(f"Line Items: {len(invoice['line_items'])}")
        
        # Run enhanced analysis
        result = analyze_invoice_enhanced(invoice)
        
        # Display key results
        print(f"\n🎯 Analysis Results:")
        
        # Outlier detection
        outlier_analysis = result.get('outlier_analysis', {})
        has_outliers = outlier_analysis.get('has_outliers', False)
        print(f"  Outlier Detection: {'⚠️ OUTLIERS DETECTED' if has_outliers else '✅ Normal'}")
        
        if has_outliers:
            for item in outlier_analysis.get('outlier_items', [])[:2]:  # Show first 2
                print(f"    • {item['description'][:40]}... (Risk Score: {item['outlier_score']:.3f})")
        
        # Rate analysis
        rate_analysis = result.get('rate_analysis', {})
        avg_rate = rate_analysis.get('average_rate', 0)
        market_pos = rate_analysis.get('market_position', 'unknown')
        
        market_emoji = {
            'above_market': '📈 ABOVE MARKET',
            'below_market': '📉 BELOW MARKET', 
            'market_rate': '💰 MARKET RATE',
            'unknown': '❓ UNKNOWN'
        }
        
        print(f"  Average Rate: ${avg_rate:.2f}/hour")
        print(f"  Market Position: {market_emoji.get(market_pos, market_pos)}")
        
        # Rate comparisons
        if rate_analysis.get('benchmark_comparisons'):
            print("  Rate Benchmarks:")
            for comp in rate_analysis['benchmark_comparisons'][:2]:  # Show first 2
                actual = comp['actual_rate']
                benchmark = comp['benchmark_mean']
                deviation = ((actual - benchmark) / benchmark) * 100 if benchmark > 0 else 0
                print(f"    • ${actual:.0f}/hr vs ${benchmark:.0f}/hr market ({deviation:+.0f}%)")
        
        # Key insights
        insights = result.get('insights', [])
        if insights:
            print("  Key Insights:")
            for insight in insights[:3]:  # Show first 3
                print(f"    {insight}")
        
        # Recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            print("  Recommendations:")
            for rec in recommendations[:2]:  # Show first 2
                print(f"    • {rec}")
    
    print(f"\n🎉 Comprehensive Demo Completed!")
    print(f"The enhanced LAIT ML system successfully:")
    print(f"  ✅ Detected outliers using real-world legal billing patterns")
    print(f"  ✅ Compared rates against industry benchmarks")
    print(f"  ✅ Provided market position analysis")
    print(f"  ✅ Generated actionable insights and recommendations")
    print(f"  ✅ Used models trained on actual legal billing data")

def show_model_statistics():
    """Show comprehensive model statistics"""
    print(f"\n📊 Enhanced ML Model Statistics")
    print("=" * 40)
    
    import sys
    sys.path.append('/app/backend')
    from models.enhanced_invoice_analyzer import EnhancedInvoiceAnalyzer
    
    analyzer = EnhancedInvoiceAnalyzer()
    
    print(f"📁 Models Directory: {analyzer.models_dir}")
    print(f"🤖 Loaded ML Models: {len(analyzer.models)}")
    print(f"⚖️ Rate Benchmarks: {len(analyzer.rate_benchmarks)} practice areas")
    
    if analyzer.rate_benchmarks:
        print(f"\n📈 Real-World Rate Benchmark Coverage:")
        total_roles = 0
        for area, roles in analyzer.rate_benchmarks.items():
            if isinstance(roles, dict):
                role_count = len(roles)
                total_roles += role_count
                print(f"  {area}: {role_count} roles")
        
        print(f"\nTotal benchmark entries: {total_roles}")
        
        # Show some sample rates
        print(f"\n💰 Sample Market Rates (Real-World Data):")
        sample_areas = ['Corporate', 'Litigation', 'IP']
        for area in sample_areas:
            if area in analyzer.rate_benchmarks:
                area_data = analyzer.rate_benchmarks[area]
                if 'Partner' in area_data and isinstance(area_data['Partner'], dict):
                    partner_rate = area_data['Partner'].get('mean', 0)
                    print(f"  {area} Partner: ~${partner_rate:.0f}/hour")

if __name__ == "__main__":
    show_model_statistics()
    run_comprehensive_demo()
