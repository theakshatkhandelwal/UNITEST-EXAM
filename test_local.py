#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Testing Script for UniTest
Run this to quickly test your local setup before deploying
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def check_env_file():
    """Check if .env file exists"""
    if not Path('.env').exists():
        print("⚠️  .env file not found!")
        print("📝 Creating .env from env_example.txt...")
        if Path('env_example.txt').exists():
            with open('env_example.txt', 'r') as f:
                content = f.read()
            with open('.env', 'w') as f:
                f.write(content)
            print("✅ Created .env file. Please update it with your API keys!")
            return False
        else:
            print("❌ env_example.txt not found!")
            return False
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("📦 Checking dependencies...")
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import google.generativeai
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def check_database_config():
    """Check if database is configured for local development"""
    print("🗄️  Checking database configuration...")
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            if 'sqlite:///' in content or 'DATABASE_URL' not in content:
                print("✅ Using local SQLite database (safe for testing)")
                return True
            elif 'postgresql://' in content or 'postgres://' in content:
                print("⚠️  Warning: Using PostgreSQL database!")
                print("💡 For local testing, use: DATABASE_URL=sqlite:///unittest_local.db")
                response = input("Continue anyway? (y/n): ")
                return response.lower() == 'y'
    return True

def test_server():
    """Test if server can start"""
    print("🚀 Testing server startup...")
    try:
        # Try to import app
        sys.path.insert(0, os.getcwd())
        from app import app
        
        # Test basic configuration
        with app.app_context():
            print("✅ Flask app loads successfully")
            print(f"✅ Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Error loading app: {e}")
        print("💡 Check your app.py for errors")
        return False

def main():
    """Main testing function"""
    print("=" * 50)
    print("🧪 UniTest Local Testing Script")
    print("=" * 50)
    print()
    
    checks = [
        ("Environment file", check_env_file),
        ("Dependencies", check_dependencies),
        ("Database config", check_database_config),
        ("Server startup", test_server),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        result = check_func()
        results.append((name, result))
        if not result:
            print(f"\n❌ {name} check failed!")
            print("💡 Please fix the issues above before proceeding")
            return False
    
    print("\n" + "=" * 50)
    print("✅ All checks passed!")
    print("=" * 50)
    print()
    print("🚀 Ready to test locally!")
    print()
    print("Next steps:")
    print("1. Run: py run_local.py  (or: py app.py)")
    print("2. Open: http://localhost:5000")
    print("3. Test your changes")
    print("4. If everything works, commit and push")
    print()
    print("💡 On Windows, use 'py' instead of 'python'")
    print()
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

