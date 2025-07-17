#!/usr/bin/env python3
"""
Test Facebook API Connection
Script untuk testing koneksi Facebook API secara langsung
"""

import os
import sys
from pathlib import Path

def test_facebook_connection():
    """Test Facebook API connection directly"""
    print("🔍 Testing Facebook API Connection...")
    print("=" * 50)
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment loaded")
    except ImportError:
        print("❌ python-dotenv not installed")
        return False
    
    # Get credentials
    page_id = os.getenv('PAGE_ID')
    page_access_token = os.getenv('PAGE_ACCESS_TOKEN')
    
    print(f"📄 PAGE_ID: {'✅ Found' if page_id else '❌ Not found'}")
    print(f"📄 PAGE_ACCESS_TOKEN: {'✅ Found' if page_access_token else '❌ Not found'}")
    
    if not page_id or not page_access_token:
        print("❌ Missing credentials")
        return False
    
    print(f"📄 Page ID: {page_id}")
    print(f"📄 Token length: {len(page_access_token)}")
    
    # Test API connection
    try:
        import requests
        
        # Test 1: Basic API call
        print("\n🔍 Testing basic API call...")
        response = requests.get(
            "https://graph.facebook.com/v18.0/me",
            params={'access_token': page_access_token}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response: {data}")
            
            if 'error' in data:
                print(f"❌ API Error: {data['error']}")
                return False
            else:
                print(f"✅ Connected as: {data.get('name', 'Unknown')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False
        
        # Test 2: Page posts
        print("\n🔍 Testing page posts...")
        response = requests.get(
            f"https://graph.facebook.com/v18.0/{page_id}/posts",
            params={
                'access_token': page_access_token,
                'fields': 'id,message,created_time',
                'limit': 1
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                print(f"✅ Found {len(data['data'])} posts")
                if data['data']:
                    post = data['data'][0]
                    print(f"📄 Sample post ID: {post.get('id', 'N/A')}")
            else:
                print(f"❌ No posts data: {data}")
        else:
            print(f"❌ Posts API Error: {response.status_code}")
            print(f"❌ Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_facebook_class():
    """Test the FacebookAPI class from streamlit_facebook.py"""
    print("\n🔍 Testing FacebookAPI Class...")
    print("=" * 50)
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get credentials
        page_id = os.getenv('PAGE_ID')
        page_access_token = os.getenv('PAGE_ACCESS_TOKEN')
        
        if not page_id or not page_access_token:
            print("❌ Missing credentials")
            return False
        
        # Import and test FacebookAPI class
        from src.app.streamlit_facebook import FacebookAPI
        
        print("✅ FacebookAPI class imported")
        
        # Create instance (this will test connection)
        api = FacebookAPI(page_id, page_access_token)
        print("✅ FacebookAPI instance created successfully")
        
        # Test get_recent_posts
        posts = api.get_recent_posts(limit=1)
        print(f"✅ Retrieved {len(posts)} posts")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing FacebookAPI class: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_app_controller_loading():
    """Test how app_controller loads environment"""
    print("\n🔍 Testing App Controller Environment Loading...")
    print("=" * 50)
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # Simulate app_controller environment loading
        from dotenv import load_dotenv
        
        # Test the exact path used in app_controller
        env_path = os.path.join(os.path.dirname(__file__), 'src', 'app', '..', '..', '.env')
        env_path = os.path.normpath(env_path)
        
        print(f"📄 App controller env path: {env_path}")
        print(f"📄 Path exists: {os.path.exists(env_path)}")
        
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print("✅ Environment loaded using app_controller path")
            
            page_id = os.getenv('PAGE_ID')
            page_access_token = os.getenv('PAGE_ACCESS_TOKEN')
            
            print(f"📄 PAGE_ID: {'✅ Found' if page_id else '❌ Not found'}")
            print(f"📄 PAGE_ACCESS_TOKEN: {'✅ Found' if page_access_token else '❌ Not found'}")
            
            return bool(page_id and page_access_token)
        else:
            print("❌ Environment file not found at app_controller path")
            return False
        
    except Exception as e:
        print(f"❌ Error testing app_controller loading: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 Facebook API Connection Test")
    print("=" * 50)
    
    tests = [
        ("Direct API Connection", test_facebook_connection),
        ("FacebookAPI Class", test_streamlit_facebook_class),
        ("App Controller Loading", test_app_controller_loading)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Error in {test_name}: {str(e)}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*20} Test Summary {'='*20}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Facebook API should work correctly.")
    else:
        print("⚠️ Some tests failed. Check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
