#!/usr/bin/env python3
"""
Test script untuk memverifikasi deployment readiness
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test semua import yang diperlukan"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    # Test optional imports
    try:
        import torch
        print("✅ PyTorch imported successfully")
    except ImportError:
        print("⚠️ PyTorch not available (optional)")
    
    try:
        import transformers
        print("✅ Transformers imported successfully")
    except ImportError:
        print("⚠️ Transformers not available (optional)")
    
    return True

def test_project_structure():
    """Test struktur proyek"""
    print("\n📁 Testing project structure...")
    
    required_files = [
        "streamlit_app.py",
        "requirements.txt",
        ".streamlit/config.toml",
        "src/app/app_controller.py",
        "src/app/streamlit_app.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    return True

def test_app_import():
    """Test import aplikasi utama"""
    print("\n🚀 Testing app import...")
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from src.app.app_controller import StreamlitJudolRemover
        print("✅ App controller imported successfully")
        return True
    except ImportError as e:
        print(f"❌ App import failed: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("\n🔧 Testing environment...")
    
    # Check for .env file
    if Path('.env').exists():
        print("✅ .env file found")
    else:
        print("⚠️ .env file not found (will use secrets in cloud)")
    
    # Check for secrets template
    if Path('.streamlit/secrets.toml').exists():
        print("✅ Secrets template found")
    else:
        print("⚠️ Secrets template not found")
    
    return True

def main():
    """Main test function"""
    print("🛡️ Judol Remover - Deployment Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Project Structure", test_project_structure),
        ("App Import", test_app_import),
        ("Environment", test_environment)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment.")
        return True
    else:
        print("⚠️ Some tests failed. Please fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
