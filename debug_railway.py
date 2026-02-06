#!/usr/bin/env python3
"""
Debug script for Railway deployment
Run this to test if the app starts correctly
"""

import os
import sys

def debug_environment():
    print("=== ENVIRONMENT DEBUG ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"PORT: {os.environ.get('PORT', 'NOT SET')}")
    print(f"DATABASE_URL: {'SET' if os.environ.get('DATABASE_URL') else 'NOT SET'}")
    print(f"SECRET_KEY: {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}")
    print()

def test_imports():
    print("=== TESTING IMPORTS ===")
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False

    try:
        from app import create_app
        print("✅ App import successful")
    except ImportError as e:
        print(f"❌ App import failed: {e}")
        return False
    
    return True

def test_app_creation():
    print("=== TESTING APP CREATION ===")
    try:
        from app import create_app
        app = create_app()
        print("✅ App created successfully")
        
        # Test health endpoint
        with app.test_client() as client:
            response = client.get('/health')
            print(f"✅ Health check: {response.status_code} - {response.get_json()}")
            
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

if __name__ == "__main__":
    debug_environment()
    
    if not test_imports():
        sys.exit(1)
    
    if not test_app_creation():
        sys.exit(1)
    
    print("\n✅ All tests passed - app should work in Railway")