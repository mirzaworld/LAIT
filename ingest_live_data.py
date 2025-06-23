#!/usr/bin/env python3
"""
Live Data Ingestion Script
Populates the live data cache with real legal industry insights
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from services.production_live_data_service import production_service

async def main():
    """Main ingestion function"""
    print("🚀 Starting Live Legal Data Ingestion...")
    
    try:
        # Fetch live data from all sources
        insights = await production_service.fetch_live_data()
        
        print(f"✅ Successfully collected {len(insights)} insights")
        
        # Get service status
        status = production_service.get_service_status()
        print(f"📊 Service Status: {status['service_status']}")
        print(f"🔗 Active Sources: {status['active_sources']}/{status['total_sources']}")
        print(f"📈 Total Insights: {status['total_insights']}")
        print(f"🕐 Recent Insights (24h): {status['recent_insights_24h']}")
        
        # Display sample insights
        recent_insights = production_service.get_recent_insights(5)
        print("\n📋 Sample Recent Insights:")
        for i, insight in enumerate(recent_insights[:3], 1):
            print(f"{i}. {insight['title']}")
            print(f"   Category: {insight['category']}")
            print(f"   Impact: {insight['impact_score']:.1f}/1.0")
            print(f"   Source: {insight['source']}")
            print()
        
    except Exception as e:
        print(f"❌ Error during data ingestion: {str(e)}")
        return 1
    
    finally:
        await production_service.close()
    
    print("✅ Live data ingestion completed successfully!")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
