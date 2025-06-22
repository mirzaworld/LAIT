#!/usr/bin/env python3
"""
LAIT Unified Application Starter
This script ensures we start the unified application with proper configuration
"""

import os
import sys
import subprocess

def main():
    # Ensure we're in the right directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Add project root to Python path
    sys.path.insert(0, project_root)
    
    # Set environment variables for consistency
    os.environ['PYTHONPATH'] = project_root
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_APP'] = 'backend/unified_app.py'
    
    print("🚀 Starting LAIT Unified Application")
    print(f"📁 Project Root: {project_root}")
    print(f"🐍 Python Path: {sys.path[0]}")
    
    # Import and run the unified app
    try:
        sys.path.insert(0, os.path.join(project_root, 'backend'))
        from unified_app import app, socketio
        
        # Configuration
        host = os.environ.get('API_HOST', '0.0.0.0')
        port = int(os.environ.get('API_PORT', 5003))
        debug = os.environ.get('DEBUG', 'True').lower() == 'true'
        
        print(f"🌐 Server starting on http://{host}:{port}")
        print(f"🔐 Demo Login: admin@lait.com / admin123")
        print(f"📊 Frontend should connect to: http://localhost:{port}")
        
        # Start the server
        socketio.run(app, host=host, port=port, debug=debug)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Trying alternative import method...")
        
        # Fallback: run the unified app directly
        unified_app_path = os.path.join(project_root, 'backend', 'unified_app.py')
        subprocess.run([sys.executable, unified_app_path])
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
