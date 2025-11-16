#!/usr/bin/env python3
"""
Local Development Server Runner
Use this script to run the app in development mode with better error messages
"""

import os
import sys

# Set development environment
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

# Check if .env exists
if not os.path.exists('.env'):
    print("⚠️  .env file not found!")
    print("📝 Creating .env from env_example.txt...")
    if os.path.exists('env_example.txt'):
        with open('env_example.txt', 'r') as f:
            content = f.read()
        with open('.env', 'w') as f:
            f.write(content)
        print("✅ Created .env file. Please update it with your API keys!")
        print("💡 Edit .env file and add your GOOGLE_AI_API_KEY")
        sys.exit(1)
    else:
        print("❌ env_example.txt not found!")
        sys.exit(1)

# Import and run the app
try:
    from app import app
    
    print("=" * 60)
    print("🚀 Starting UniTest Local Development Server")
    print("=" * 60)
    print()
    print("📍 Server will run at: http://localhost:5000")
    print("🔧 Debug mode: ENABLED")
    print("⚠️  Press Ctrl+C to stop the server")
    print()
    print("-" * 60)
    print()
    
    # Run the app
    app.run(host='127.0.0.1', port=5000, debug=True)
    
except KeyboardInterrupt:
    print("\n\n👋 Server stopped by user")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ Error starting server: {e}")
    print("\n💡 Troubleshooting:")
    print("1. Check if .env file has correct API keys")
    print("2. Run: pip install -r requirements.txt")
    print("3. Check for errors in app.py")
    sys.exit(1)

