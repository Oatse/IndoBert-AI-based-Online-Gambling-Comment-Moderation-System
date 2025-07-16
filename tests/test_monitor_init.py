#!/usr/bin/env python3
"""
Test script untuk memverifikasi inisialisasi Auto Monitor
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test semua import yang diperlukan"""
    print("🔍 Testing imports...")
    
    try:
        from streamlit_facebook import FacebookAPI
        print("✅ FacebookAPI import successful")
    except Exception as e:
        print(f"❌ FacebookAPI import failed: {e}")
        return False
    
    try:
        from spam_detector import SpamDetector
        print("✅ SpamDetector import successful")
    except Exception as e:
        print(f"❌ SpamDetector import failed: {e}")
        return False
    
    try:
        from streamlit_monitor import AutoMonitor
        print("✅ AutoMonitor import successful")
    except Exception as e:
        print(f"❌ AutoMonitor import failed: {e}")
        return False
    
    return True

def test_facebook_api():
    """Test Facebook API initialization"""
    print("\n🔍 Testing Facebook API...")
    
    page_id = os.getenv('PAGE_ID')
    page_access_token = os.getenv('PAGE_ACCESS_TOKEN')
    
    if not page_id or not page_access_token:
        print("❌ Missing Facebook credentials in .env")
        print(f"PAGE_ID: {'✅' if page_id else '❌'}")
        print(f"PAGE_ACCESS_TOKEN: {'✅' if page_access_token else '❌'}")
        return None
    
    try:
        from streamlit_facebook import FacebookAPI
        facebook_api = FacebookAPI(page_id, page_access_token)
        print("✅ Facebook API initialized successfully")
        
        # Test connection
        posts = facebook_api.get_recent_posts(limit=1)
        print(f"✅ Facebook API connection test successful ({len(posts)} posts)")
        return facebook_api
        
    except Exception as e:
        print(f"❌ Facebook API initialization failed: {e}")
        return None

def test_spam_detector():
    """Test Spam Detector initialization"""
    print("\n🔍 Testing Spam Detector...")
    
    model_path = os.getenv('MODEL_PATH', './python/models')
    
    if not os.path.exists(model_path):
        print(f"❌ Model path not found: {model_path}")
        return None
    
    try:
        from spam_detector import SpamDetector
        spam_detector = SpamDetector(model_path)
        print("✅ Spam Detector initialized successfully")
        
        # Test prediction
        test_text = "This is a test comment"
        prediction = spam_detector.predict(test_text)
        print(f"✅ Spam Detector test successful (confidence: {prediction['confidence']:.3f})")
        return spam_detector
        
    except Exception as e:
        print(f"❌ Spam Detector initialization failed: {e}")
        return None

def test_auto_monitor(facebook_api, spam_detector):
    """Test Auto Monitor initialization"""
    print("\n🔍 Testing Auto Monitor...")
    
    if not facebook_api:
        print("❌ Cannot test Auto Monitor: Facebook API not available")
        return None
    
    if not spam_detector:
        print("❌ Cannot test Auto Monitor: Spam Detector not available")
        return None
    
    try:
        from streamlit_monitor import AutoMonitor
        auto_monitor = AutoMonitor(facebook_api, spam_detector, poll_interval=30)
        print("✅ Auto Monitor initialized successfully")
        
        # Test status
        status = auto_monitor.get_status()
        print(f"✅ Auto Monitor status check successful")
        print(f"   - Running: {status['is_running']}")
        print(f"   - Poll Interval: {status['poll_interval']}s")
        
        return auto_monitor
        
    except Exception as e:
        print(f"❌ Auto Monitor initialization failed: {e}")
        return None

def test_monitor_start_stop(auto_monitor):
    """Test Auto Monitor start/stop functionality"""
    print("\n🔍 Testing Auto Monitor start/stop...")
    
    if not auto_monitor:
        print("❌ Cannot test start/stop: Auto Monitor not available")
        return False
    
    try:
        # Test start
        print("🔄 Starting monitor...")
        auto_monitor.start()
        
        status = auto_monitor.get_status()
        if status['is_running']:
            print("✅ Monitor started successfully")
        else:
            print("❌ Monitor failed to start")
            return False
        
        # Test stop
        print("🔄 Stopping monitor...")
        auto_monitor.stop()
        
        status = auto_monitor.get_status()
        if not status['is_running']:
            print("✅ Monitor stopped successfully")
        else:
            print("❌ Monitor failed to stop")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Monitor start/stop test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Auto Monitor Initialization Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Cannot continue.")
        sys.exit(1)
    
    # Test Facebook API
    facebook_api = test_facebook_api()
    
    # Test Spam Detector
    spam_detector = test_spam_detector()
    
    # Test Auto Monitor
    auto_monitor = test_auto_monitor(facebook_api, spam_detector)
    
    # Test start/stop
    start_stop_success = test_monitor_start_stop(auto_monitor)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"✅ Imports: {'PASS' if True else 'FAIL'}")
    print(f"{'✅' if facebook_api else '❌'} Facebook API: {'PASS' if facebook_api else 'FAIL'}")
    print(f"{'✅' if spam_detector else '❌'} Spam Detector: {'PASS' if spam_detector else 'FAIL'}")
    print(f"{'✅' if auto_monitor else '❌'} Auto Monitor: {'PASS' if auto_monitor else 'FAIL'}")
    print(f"{'✅' if start_stop_success else '❌'} Start/Stop: {'PASS' if start_stop_success else 'FAIL'}")
    
    if facebook_api and spam_detector and auto_monitor and start_stop_success:
        print("\n🎉 All tests passed! Auto Monitor should work correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
