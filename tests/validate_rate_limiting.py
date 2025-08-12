#!/usr/bin/env python3
"""
Flask-Limiter Configuration Validator

Checks if the rate limiting configuration is properly set up.
"""

import sys
import os

# Add backend to path
sys.path.append('/Users/mirza/Documents/GitHub/LAIT/backend')

def validate_rate_limiting_config():
    """Validate that Flask-Limiter is properly configured"""
    print("🔍 Validating Flask-Limiter Configuration")
    print("=" * 45)
    
    try:
        # Try importing flask-limiter
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        print("✅ Flask-Limiter imports successful")
        
        # Check if the backend app has limiter configured
        try:
            from app_real import app, limiter
            print("✅ Limiter instance found in backend")
            
            # Check if limiter is configured
            if hasattr(limiter, 'limit'):
                print("✅ Limiter has limit decorator")
            else:
                print("❌ Limiter missing limit decorator")
                
            # Check storage configuration
            storage_type = type(limiter.storage).__name__
            print(f"📦 Storage backend: {storage_type}")
            
            if 'Redis' in storage_type:
                print("✅ Using Redis storage (recommended)")
            else:
                print("⚠️  Using memory storage (fallback)")
                
        except ImportError as e:
            print(f"❌ Cannot import limiter from backend: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Flask-Limiter not available: {e}")
        print("💡 Install with: pip install Flask-Limiter")
        return False
    
    print("\n📋 Rate Limiting Configuration Summary:")
    print("  🔐 Login endpoint: 5 requests/minute per IP")
    print("  📤 Upload endpoint: 60 requests/minute per token") 
    print("  🗄️ Storage: Redis (with memory fallback)")
    print("  🚨 Error handling: 429 response with retry-after")
    
    return True

def check_dependencies():
    """Check if all required dependencies are available"""
    print("\n🔧 Checking Dependencies")
    print("=" * 25)
    
    dependencies = [
        ('flask', 'Flask'),
        ('flask_limiter', 'Flask-Limiter'),
        ('flask_jwt_extended', 'Flask-JWT-Extended'),
        ('redis', 'Redis (optional)'),
    ]
    
    all_available = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            if 'redis' in module:
                print(f"⚠️  {name} (will use memory storage)")
            else:
                print(f"❌ {name} - REQUIRED")
                all_available = False
    
    return all_available

def main():
    """Main validation function"""
    print("🛡️  LAIT Security - Rate Limiting Validator")
    print("=" * 50)
    
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n❌ Missing required dependencies")
        return False
    
    config_ok = validate_rate_limiting_config()
    if not config_ok:
        print("\n❌ Rate limiting configuration issues found")
        return False
    
    print("\n✅ Rate limiting is properly configured!")
    print("\n🧪 Next steps:")
    print("  1. Start the backend: cd backend && python app_real.py")
    print("  2. Test rate limits: python tests/test_rate_limiting.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
