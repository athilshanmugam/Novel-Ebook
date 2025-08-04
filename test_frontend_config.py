#!/usr/bin/env python3
"""
Test script to verify frontend configuration and API endpoints
"""

import requests
import json
import sys
import os

def test_api_endpoints():
    """Test API endpoints to ensure they're working"""
    
    # Test both local and production URLs
    urls = [
        'http://localhost:5000',
        'https://novel-ebook.onrender.com'
    ]
    
    print("🧪 Testing API Endpoints...")
    print("=" * 50)
    
    for base_url in urls:
        print(f"\n📍 Testing: {base_url}")
        print("-" * 30)
        
        try:
            # Test basic connectivity
            response = requests.get(f"{base_url}/", timeout=10)
            print(f"✅ Root endpoint: {response.status_code}")
            
            # Test admin stats endpoint
            response = requests.get(f"{base_url}/api/admin/stats", timeout=10)
            print(f"✅ Admin stats: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   📊 Users: {data['stats']['total_users']}")
                    print(f"   📖 Sessions: {data['stats']['total_sessions']}")
                    print(f"   📄 Pages: {data['stats']['total_pages_read']}")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection failed: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_frontend_files():
    """Test if frontend files exist and are accessible"""
    
    print("\n🧪 Testing Frontend Files...")
    print("=" * 50)
    
    frontend_files = [
        'frontend/index.html',
        'frontend/admin.html', 
        'frontend/script.js',
        'frontend/config.js'
    ]
    
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing!")

def test_configuration():
    """Test configuration files"""
    
    print("\n🧪 Testing Configuration...")
    print("=" * 50)
    
    config_files = [
        'config.py',
        'requirements.txt',
        'create_env.py'
    ]
    
    for file_path in config_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing!")

def main():
    """Run all tests"""
    print("🚀 Frontend Configuration Test Suite")
    print("=" * 50)
    
    test_configuration()
    test_frontend_files()
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\n📝 Next steps:")
    print("1. Run: python create_env.py")
    print("2. Run: python app.py")
    print("3. Visit: http://localhost:5000/frontend/")
    print("4. Admin: http://localhost:5000/frontend/admin.html")

if __name__ == "__main__":
    main() 