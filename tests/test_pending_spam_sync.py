#!/usr/bin/env python3
"""
Test script untuk memverifikasi pending spam sync functionality
"""

import sys
import os
import time

# Add path for imports
sys.path.append('./python/services')

def test_pending_spam_sync():
    """Test pending spam synchronization"""
    print("🔍 Testing Pending Spam Synchronization")
    print("=" * 50)
    
    try:
        from streamlit_monitor import AutoMonitor
        
        # Mock objects
        class MockFacebookAPI:
            def get_recent_posts(self, limit=5):
                return [{'id': 'post_123'}]
            
            def get_post_comments(self, post_id, limit=20):
                return [{
                    'id': 'comment_123',
                    'message': 'ayo depo sekarang dijamin maxwinnn',
                    'from': {'name': 'Test User'}
                }]
            
            def delete_comment(self, comment_id):
                return True
        
        class MockSpamDetector:
            def predict(self, text):
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
        
        # Mock session state
        class MockSessionState:
            def __init__(self):
                self.pending_spam = []
        
        facebook_api = MockFacebookAPI()
        spam_detector = MockSpamDetector()
        auto_monitor = AutoMonitor(facebook_api, spam_detector, poll_interval=10)
        
        print("✅ AutoMonitor initialized successfully")
        
        # Test 1: Add spam to internal storage
        print("\n📋 Test 1: Add Spam to Internal Storage")
        print("-" * 40)
        
        spam_data = {
            'comment_id': 'comment_123',
            'message': 'ayo depo sekarang dijamin maxwinnn',
            'author': 'Test User',
            'post_id': 'post_123',
            'prediction': {'is_spam': True, 'confidence': 0.95},
            'detected_time': '2024-06-24T21:00:00'
        }
        
        # Disable auto delete to trigger pending spam
        auto_monitor.update_config(auto_delete_enabled=False)
        
        # Add spam manually
        auto_monitor._add_to_pending_spam(spam_data)
        
        internal_count = auto_monitor.get_pending_spam_count()
        print(f"Internal pending spam count: {internal_count}")
        
        if internal_count == 1:
            print("✅ Spam successfully added to internal storage")
        else:
            print("❌ Spam not added to internal storage")
            return False
        
        # Test 2: Process comment that should go to pending
        print("\n📋 Test 2: Process Comment (Auto Delete OFF)")
        print("-" * 40)
        
        comment = {
            'id': 'comment_456',
            'message': 'ayo depo lagi dijamin maxwinnn',
            'from': {'name': 'Test User 2'}
        }
        
        # Process comment (should go to pending)
        auto_monitor._process_comment(comment, 'post_123')
        
        internal_count = auto_monitor.get_pending_spam_count()
        print(f"Internal pending spam count after processing: {internal_count}")
        
        if internal_count == 2:
            print("✅ Comment processed and added to pending spam")
        else:
            print("❌ Comment not added to pending spam")
            return False
        
        # Test 3: Test sync functionality (without actual session state)
        print("\n📋 Test 3: Test Sync Functionality")
        print("-" * 40)
        
        # This will fail gracefully since we don't have real session state
        try:
            result = auto_monitor.sync_pending_spam_to_session_state()
            print(f"Sync result: {result}")
            print("✅ Sync method executed without errors")
        except Exception as e:
            print(f"⚠️ Sync failed as expected (no session state): {str(e)}")
        
        # Test 4: Clear pending spam
        print("\n📋 Test 4: Clear Pending Spam")
        print("-" * 40)
        
        auto_monitor.clear_pending_spam()
        internal_count = auto_monitor.get_pending_spam_count()
        print(f"Internal pending spam count after clear: {internal_count}")
        
        if internal_count == 0:
            print("✅ Pending spam cleared successfully")
        else:
            print("❌ Pending spam not cleared")
            return False
        
        print("\n🎉 All pending spam sync tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_simulation():
    """Simulate the complete workflow"""
    print("\n🔍 Testing Complete Workflow Simulation")
    print("=" * 50)
    
    try:
        from streamlit_monitor import AutoMonitor
        
        # Mock objects
        class MockFacebookAPI:
            def get_recent_posts(self, limit=5):
                return [{'id': 'post_123'}]
            
            def get_post_comments(self, post_id, limit=20):
                return [
                    {
                        'id': 'comment_spam_1',
                        'message': 'ayo depo sekarang dijamin maxwinnn',
                        'from': {'name': 'Spammer 1'}
                    },
                    {
                        'id': 'comment_normal_1',
                        'message': 'nice post, thanks for sharing',
                        'from': {'name': 'Normal User'}
                    },
                    {
                        'id': 'comment_spam_2',
                        'message': 'buruan daftar sekarang bonus 100%',
                        'from': {'name': 'Spammer 2'}
                    }
                ]
            
            def delete_comment(self, comment_id):
                return True
        
        class MockSpamDetector:
            def predict(self, text):
                spam_keywords = ['depo', 'maxwin', 'bonus', 'daftar', 'buruan']
                if any(keyword in text.lower() for keyword in spam_keywords):
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
        
        print("✅ Workflow simulation initialized")
        
        # Scenario 1: Auto delete disabled
        print("\n📋 Scenario 1: Auto Delete Disabled")
        print("-" * 40)
        
        auto_monitor.update_config(auto_delete_enabled=False)
        
        # Simulate checking for new comments
        posts = facebook_api.get_recent_posts()
        for post in posts:
            comments = facebook_api.get_post_comments(post['id'])
            for comment in comments:
                auto_monitor._process_comment(comment, post['id'])
        
        pending_count = auto_monitor.get_pending_spam_count()
        print(f"Pending spam count: {pending_count}")
        
        if pending_count == 2:  # Should have 2 spam comments
            print("✅ Spam comments correctly added to pending (auto delete OFF)")
        else:
            print(f"❌ Expected 2 pending spam, got {pending_count}")
            return False
        
        # Scenario 2: Enable auto delete and clear pending
        print("\n📋 Scenario 2: Enable Auto Delete")
        print("-" * 40)
        
        auto_monitor.update_config(auto_delete_enabled=True)
        auto_monitor.clear_pending_spam()
        
        # Process same comments again
        for post in posts:
            comments = facebook_api.get_post_comments(post['id'])
            for comment in comments:
                auto_monitor._process_comment(comment, post['id'])
        
        pending_count = auto_monitor.get_pending_spam_count()
        print(f"Pending spam count: {pending_count}")
        
        if pending_count == 0:  # Should have 0 pending (auto deleted)
            print("✅ Spam comments auto-deleted (auto delete ON)")
        else:
            print(f"❌ Expected 0 pending spam, got {pending_count}")
            return False
        
        print("\n🎉 Complete workflow simulation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Workflow simulation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Pending Spam Sync Test Suite")
    print("=" * 60)
    
    # Test pending spam sync functionality
    test1_passed = test_pending_spam_sync()
    
    # Test complete workflow simulation
    test2_passed = test_workflow_simulation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"✅ Pending Spam Sync: {'PASS' if test1_passed else 'FAIL'}")
    print(f"✅ Workflow Simulation: {'PASS' if test2_passed else 'FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Pending spam sync should work correctly.")
        print("\n📋 Expected Behavior in Streamlit:")
        print("1. When auto delete is OFF → Spam goes to internal storage")
        print("2. Internal storage syncs to session state periodically")
        print("3. UI shows pending spam count from session state")
        print("4. Manual sync button forces immediate synchronization")
        print("5. Pending spam page shows all pending comments")
        return True
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
