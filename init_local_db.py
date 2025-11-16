#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialize Local Database
Run this script to create all database tables for local development
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Set development environment
os.environ['FLASK_ENV'] = 'development'

# Check if .env exists
if not os.path.exists('.env'):
    print("⚠️  .env file not found!")
    print("📝 Please create .env file first")
    print("💡 Copy env_example.txt to .env and add your API keys")
    sys.exit(1)

print("=" * 60)
print("🗄️  Initializing Local Database")
print("=" * 60)
print()

try:
    from app import app, db, init_db
    
    with app.app_context():
        print("📋 Creating database tables...")
        print()
        
        # Initialize database
        init_db()
        
        print()
        print("=" * 60)
        print("✅ Database initialized successfully!")
        print("=" * 60)
        print()
        print("📝 Next steps:")
        print("1. Run: py run_local.py")
        print("2. Open: http://localhost:5000")
        print("3. Sign up for a new account")
        print("4. Start testing your changes!")
        print()
        
except Exception as e:
    print(f"❌ Error initializing database: {e}")
    print()
    print("💡 Troubleshooting:")
    print("1. Make sure .env file exists with DATABASE_URL")
    print("2. For local testing, use: DATABASE_URL=sqlite:///unittest_local.db")
    print("3. Check if database file is not locked by another process")
    sys.exit(1)

