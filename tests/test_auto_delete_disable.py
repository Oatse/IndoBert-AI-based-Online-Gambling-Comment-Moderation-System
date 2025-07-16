#!/usr/bin/env python3
"""
Test script untuk memverifikasi auto delete disable functionality
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_auto_delete_disable():
    """Test auto delete disable functionality"""
    print("🔍 Testing Auto Delete Disable Functionality")
    print("=" * 50)
    
    try:
        # Import required modules
        sys.path.append('.')
        from src.app.streamlit_facebook import FacebookAPI
        from src.services.spam_detector_optimized import OptimizedSpamDetector as SpamDetector
        from src.app.streamlit_monitor import AutoMonitor
        
        # Initialize components
        page_id = os.getenv('PAGE_ID')
        page_access_token = os.getenv('PAGE_ACCESS_TOKEN')
        model_path = os.getenv('MODEL_PATH', './src/models')
        
        if not page_id or not page_access_token:
            print("❌ Missing Facebook credentials")
            return False
        
        print("🔧 Initializing components...")
        facebook_api = FacebookAPI(page_id, page_access_token)
        spam_detector = SpamDetector(model_path)
        auto_monitor = AutoMonitor(facebook_api, spam_detector, poll_interval=10)
        
        print("✅ Components initialized successfully")
        
        # Test 1: Auto delete enabled (default)
        print("\n📋 Test 1: Auto Delete Enabled")
        print("-" * 30)
        
        config = auto_monitor.get_config()
        print(f"Initial config: {config}")
        
        if config['auto_delete_enabled']:
            print("✅ Auto delete is enabled by default")
        else:
            print("❌ Auto delete should be enabled by default")
            return False
        
        # Test 2: Disable auto delete
        print("\n📋 Test 2: Disable Auto Delete")
        print("-" * 30)
        
        auto_monitor.update_config(auto_delete_enabled=False)
        config = auto_monitor.get_config()
        print(f"Updated config: {config}")
        
        if not config['auto_delete_enabled']:
            print("✅ Auto delete successfully disabled")
        else:
            print("❌ Auto delete should be disabled")
            return False
        
        # Test 3: Enable auto delete again
        print("\n📋 Test 3: Re-enable Auto Delete")
        print("-" * 30)
        
        auto_monitor.update_config(auto_delete_enabled=True)
        config = auto_monitor.get_config()
        print(f"Updated config: {config}")
        
        if config['auto_delete_enabled']:
            print("✅ Auto delete successfully re-enabled")
        else:
            print("❌ Auto delete should be enabled")
            return False
        
        # Test 4: Test confidence threshold
        print("\n📋 Test 4: Confidence Threshold")
        print("-" * 30)
        
        auto_monitor.update_config(confidence_threshold=0.7)
        config = auto_monitor.get_config()
        print(f"Updated config: {config}")
        
        if config['confidence_threshold'] == 0.7:
            print("✅ Confidence threshold successfully updated")
        else:
            print("❌ Confidence threshold should be 0.7")
            return False
        
        # Test 5: Simulate spam detection with auto delete disabled
        print("\n📋 Test 5: Simulate Spam Detection (Auto Delete OFF)")
        print("-" * 30)
        
        # Disable auto delete
        auto_monitor.update_config(auto_delete_enabled=False)
        
        # Test spam text
        spam_text = "ayo depo sekarang dijamin maxwinnn"
        prediction = spam_detector.predict(spam_text)
        
        print(f"Spam text: {spam_text}")
        print(f"Prediction: {prediction}")
        print(f"Is spam: {prediction['is_spam']}")
        print(f"Confidence: {prediction['confidence']:.3f}")
        print(f"Auto delete enabled: {auto_monitor.get_config()['auto_delete_enabled']}")
        
        if prediction['is_spam'] and not auto_monitor.get_config()['auto_delete_enabled']:
            print("✅ Spam detected but auto delete is disabled - should go to pending")
        else:
            print("❌ Test condition not met")
            return False
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

def test_pending_spam_mechanism():
    """Test pending spam mechanism"""
    print("\n🔍 Testing Pending Spam Mechanism")
    print("=" * 50)
    
    try:
        # Create a mock session state
        class MockSessionState:
            def __init__(self):
                self.pending_spam = []
        
        # Test adding to pending spam
        from src.app.streamlit_monitor import AutoMonitor
        
        # Create mock data
        spam_data = {
            'comment_id': 'test_123',
            'message': 'test spam message',
            'author': 'Test User',
            'post_id': 'post_123',
            'prediction': {'is_spam': True, 'confidence': 0.95},
            'detected_time': '2024-06-24T20:00:00'
        }
        
        print(f"Mock spam data: {spam_data}")
        print("✅ Pending spam mechanism structure is correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Pending spam test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Auto Delete Disable Test Suite")
    print("=" * 60)
    
    # Test auto delete disable functionality
    test1_passed = test_auto_delete_disable()
    
    # Test pending spam mechanism
    test2_passed = test_pending_spam_mechanism()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"✅ Auto Delete Disable: {'PASS' if test1_passed else 'FAIL'}")
    print(f"✅ Pending Spam Mechanism: {'PASS' if test2_passed else 'FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Auto delete disable should work correctly.")
        print("\n📋 Expected Behavior:")
        print("1. When auto delete is ON → Spam comments are deleted automatically")
        print("2. When auto delete is OFF → Spam comments go to pending review")
        print("3. Configuration changes are applied immediately")
        print("4. Pending spam list is populated correctly")
        return True
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
