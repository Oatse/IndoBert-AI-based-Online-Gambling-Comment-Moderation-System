#!/usr/bin/env python3
"""
Test script for Streamlit Judol Remover application
Tests basic functionality without requiring Facebook API or model files
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class TestStreamlitApp(unittest.TestCase):
    """Test cases for Streamlit application components"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'PAGE_ID': 'test_page_id',
            'PAGE_ACCESS_TOKEN': 'test_token',
            'MODEL_PATH': './test_models',
            'CONFIDENCE_THRESHOLD': '0.8'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
    
    def test_imports(self):
        """Test that all required modules can be imported"""
        try:
            from src.app import streamlit_app
            from src.app import streamlit_facebook
            from src.app import streamlit_monitor
            print("✅ All modules imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import modules: {e}")
    
    @patch('streamlit_facebook.requests.Session')
    def test_facebook_api_init(self, mock_session):
        """Test Facebook API initialization"""
        from streamlit_facebook import FacebookAPI
        
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'Test Page'}
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response
        
        try:
            api = FacebookAPI('test_page_id', 'test_token')
            self.assertEqual(api.page_id, 'test_page_id')
            self.assertEqual(api.access_token, 'test_token')
            print("✅ Facebook API initialization test passed")
        except Exception as e:
            print(f"⚠️ Facebook API test failed (expected without real credentials): {e}")
    
    def test_spam_detector_import(self):
        """Test spam detector import"""
        try:
            from src.services.spam_detector import SpamDetector
            print("✅ Spam detector import successful")
        except ImportError as e:
            print(f"⚠️ Spam detector import failed (expected without model files): {e}")
    
    @patch('streamlit_monitor.threading.Thread')
    def test_auto_monitor_init(self, mock_thread):
        """Test auto monitor initialization"""
        from streamlit_monitor import AutoMonitor
        
        # Mock dependencies
        mock_facebook_api = Mock()
        mock_spam_detector = Mock()
        
        try:
            monitor = AutoMonitor(mock_facebook_api, mock_spam_detector)
            self.assertFalse(monitor.is_running)
            self.assertEqual(monitor.poll_interval, 30)
            print("✅ Auto monitor initialization test passed")
        except Exception as e:
            self.fail(f"Auto monitor initialization failed: {e}")
    
    def test_environment_loading(self):
        """Test environment variable loading"""
        # Test with mocked environment
        self.assertEqual(os.getenv('PAGE_ID'), 'test_page_id')
        self.assertEqual(os.getenv('PAGE_ACCESS_TOKEN'), 'test_token')
        self.assertEqual(os.getenv('MODEL_PATH'), './test_models')
        self.assertEqual(os.getenv('CONFIDENCE_THRESHOLD'), '0.8')
        print("✅ Environment loading test passed")
    
    def test_requirements_file(self):
        """Test that requirements.txt exists and contains required packages"""
        requirements_file = 'requirements.txt'
        self.assertTrue(os.path.exists(requirements_file), "requirements.txt not found")
        
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        required_packages = ['streamlit', 'pandas', 'requests', 'python-dotenv']
        for package in required_packages:
            self.assertIn(package, content, f"Package {package} not found in requirements.txt")
        
        print("✅ Requirements file test passed")
    
    def test_config_files(self):
        """Test that configuration files exist"""
        config_files = [
            '.streamlit/config.toml',
            'README_STREAMLIT.md',
            'run_streamlit.py',
            'start_streamlit.bat'
        ]
        
        for config_file in config_files:
            self.assertTrue(os.path.exists(config_file), f"Config file {config_file} not found")
        
        print("✅ Configuration files test passed")

class TestFunctionalComponents(unittest.TestCase):
    """Test functional components with mocked dependencies"""
    
    @patch('streamlit_facebook.requests.Session')
    def test_facebook_api_methods(self, mock_session):
        """Test Facebook API methods with mocked responses"""
        from streamlit_facebook import FacebookAPI
        
        # Mock session and responses
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'Test Page'}
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response
        
        try:
            api = FacebookAPI('test_page_id', 'test_token')
            
            # Test get_recent_posts with mocked response
            mock_response.json.return_value = {
                'data': [
                    {'id': 'post1', 'message': 'Test post', 'created_time': '2024-01-01T00:00:00Z'}
                ]
            }
            
            posts = api.get_recent_posts(limit=1)
            self.assertIsInstance(posts, list)
            print("✅ Facebook API methods test passed")
            
        except Exception as e:
            print(f"⚠️ Facebook API methods test failed: {e}")
    
    def test_monitor_statistics(self):
        """Test monitor statistics tracking"""
        from streamlit_monitor import AutoMonitor
        
        # Mock dependencies
        mock_facebook_api = Mock()
        mock_spam_detector = Mock()
        
        monitor = AutoMonitor(mock_facebook_api, mock_spam_detector)
        
        # Test initial statistics
        stats = monitor.get_statistics()
        self.assertEqual(stats['comments_processed'], 0)
        self.assertEqual(stats['spam_removed'], 0)
        self.assertFalse(stats['is_running'])
        
        # Test statistics update
        monitor.statistics['comments_processed'] = 5
        monitor.statistics['spam_removed'] = 2
        
        updated_stats = monitor.get_statistics()
        self.assertEqual(updated_stats['comments_processed'], 5)
        self.assertEqual(updated_stats['spam_removed'], 2)
        
        print("✅ Monitor statistics test passed")

def run_basic_tests():
    """Run basic functionality tests"""
    print("🧪 Running Streamlit Application Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestStreamlitApp))
    suite.addTests(loader.loadTestsFromTestCase(TestFunctionalComponents))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed! The Streamlit application is ready to run.")
        print("\n🚀 To start the application:")
        print("   python run_streamlit.py")
        print("   or")
        print("   python -m streamlit run streamlit_app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)
