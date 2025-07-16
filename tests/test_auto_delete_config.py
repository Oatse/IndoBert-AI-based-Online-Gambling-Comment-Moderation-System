#!/usr/bin/env python3
"""
Test script untuk memverifikasi auto delete configuration tanpa Facebook API
"""

import sys
import os

# Add path for imports
sys.path.append('./python/services')

def test_auto_monitor_config():
    """Test AutoMonitor configuration functionality"""
    print("🔍 Testing AutoMonitor Configuration")
    print("=" * 50)
    
    try:
        from streamlit_monitor import AutoMonitor
        
        # Create mock objects
        class MockFacebookAPI:
            def get_recent_posts(self, limit=5):
                return []
            
            def get_post_comments(self, post_id, limit=20):
                return []
            
            def delete_comment(self, comment_id):
                return True
        
        class MockSpamDetector:
            def predict(self, text):
                return {
                    'is_spam': True,
                    'confidence': 0.95,
                    'label': 'spam'
                }
        
        # Initialize AutoMonitor with mock objects
        facebook_api = MockFacebookAPI()
        spam_detector = MockSpamDetector()
        auto_monitor = AutoMonitor(facebook_api, spam_detector, poll_interval=10)
        
        print("✅ AutoMonitor initialized successfully")
        
        # Test 1: Default configuration
        print("\n📋 Test 1: Default Configuration")
        print("-" * 30)
        
        config = auto_monitor.get_config()
        print(f"Default config: {config}")
        
        expected_defaults = {
            'auto_delete_enabled': True,
            'confidence_threshold': 0.5
        }
        
        for key, expected_value in expected_defaults.items():
            if config[key] == expected_value:
                print(f"✅ {key}: {config[key]} (correct)")
            else:
                print(f"❌ {key}: {config[key]} (expected: {expected_value})")
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
        
        # Test 3: Update confidence threshold
        print("\n📋 Test 3: Update Confidence Threshold")
        print("-" * 30)
        
        auto_monitor.update_config(confidence_threshold=0.8)
        config = auto_monitor.get_config()
        print(f"Updated config: {config}")
        
        if config['confidence_threshold'] == 0.8:
            print("✅ Confidence threshold successfully updated")
        else:
            print("❌ Confidence threshold should be 0.8")
            return False
        
        # Test 4: Update both settings
        print("\n📋 Test 4: Update Both Settings")
        print("-" * 30)
        
        auto_monitor.update_config(auto_delete_enabled=True, confidence_threshold=0.6)
        config = auto_monitor.get_config()
        print(f"Updated config: {config}")
        
        if config['auto_delete_enabled'] and config['confidence_threshold'] == 0.6:
            print("✅ Both settings successfully updated")
        else:
            print("❌ Settings not updated correctly")
            return False
        
        print("\n🎉 All configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_spam_processing_logic():
    """Test spam processing logic with different configurations"""
    print("\n🔍 Testing Spam Processing Logic")
    print("=" * 50)
    
    try:
        from streamlit_monitor import AutoMonitor
        
        # Mock objects
        class MockFacebookAPI:
            def __init__(self):
                self.deleted_comments = []
            
            def get_recent_posts(self, limit=5):
                return [{'id': 'post_123'}]
            
            def get_post_comments(self, post_id, limit=20):
                return [{
                    'id': 'comment_123',
                    'message': 'ayo depo sekarang dijamin maxwinnn',
                    'from': {'name': 'Test User'}
                }]
            
            def delete_comment(self, comment_id):
                self.deleted_comments.append(comment_id)
                return True
        
        class MockSpamDetector:
            def predict(self, text):
                # Simulate spam detection
                if 'depo' in text.lower() or 'maxwin' in text.lower():
                    return {
                        'is_spam': True,
                        'confidence': 0.95,
                        'label': 'spam'
                    }
                return {
                    'is_spam': False,
                    'confidence': 0.1,
                    'label': 'normal'
                }
        
        facebook_api = MockFacebookAPI()
        spam_detector = MockSpamDetector()
        auto_monitor = AutoMonitor(facebook_api, spam_detector, poll_interval=10)
        
        # Test 1: Auto delete enabled
        print("\n📋 Test 1: Auto Delete Enabled")
        print("-" * 30)
        
        auto_monitor.update_config(auto_delete_enabled=True, confidence_threshold=0.5)
        
        # Simulate processing a comment
        comment = {
            'id': 'comment_123',
            'message': 'ayo depo sekarang dijamin maxwinnn',
            'from': {'name': 'Test User'}
        }
        
        # Process comment manually
        auto_monitor._process_comment(comment, 'post_123')
        
        if 'comment_123' in facebook_api.deleted_comments:
            print("✅ Spam comment was deleted (auto delete enabled)")
        else:
            print("❌ Spam comment should have been deleted")
            return False
        
        # Test 2: Auto delete disabled
        print("\n📋 Test 2: Auto Delete Disabled")
        print("-" * 30)
        
        # Reset
        facebook_api.deleted_comments = []
        auto_monitor.update_config(auto_delete_enabled=False)
        
        # Process another comment
        comment2 = {
            'id': 'comment_456',
            'message': 'ayo depo lagi dijamin maxwinnn',
            'from': {'name': 'Test User 2'}
        }
        
        auto_monitor._process_comment(comment2, 'post_123')
        
        if 'comment_456' not in facebook_api.deleted_comments:
            print("✅ Spam comment was NOT deleted (auto delete disabled)")
        else:
            print("❌ Spam comment should NOT have been deleted")
            return False
        
        print("\n🎉 All spam processing tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Spam processing test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Auto Delete Configuration Test Suite")
    print("=" * 60)
    
    # Test configuration functionality
    test1_passed = test_auto_monitor_config()
    
    # Test spam processing logic
    test2_passed = test_spam_processing_logic()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"✅ Configuration Tests: {'PASS' if test1_passed else 'FAIL'}")
    print(f"✅ Spam Processing Tests: {'PASS' if test2_passed else 'FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Auto delete disable functionality works correctly.")
        print("\n📋 Verified Functionality:")
        print("1. ✅ Configuration can be updated dynamically")
        print("2. ✅ Auto delete can be enabled/disabled")
        print("3. ✅ Confidence threshold can be adjusted")
        print("4. ✅ Spam comments are deleted when auto delete is ON")
        print("5. ✅ Spam comments are NOT deleted when auto delete is OFF")
        print("\n🔧 Next Steps:")
        print("1. Test in Streamlit UI with real Facebook data")
        print("2. Verify pending spam functionality")
        print("3. Check configuration synchronization")
        return True
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
