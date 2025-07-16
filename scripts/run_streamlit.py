#!/usr/bin/env python3
"""
Startup script for Judol Remover Streamlit Application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'pandas',
        'requests',
        'dotenv'  # python-dotenv imports as 'dotenv'
    ]

    # Optional packages (not required for basic functionality)
    optional_packages = [
        'torch',
        'transformers'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            # Convert back to pip package name
            pip_name = 'python-dotenv' if package == 'dotenv' else package
            print(f"   - {pip_name}")
        print("\n💡 Install missing packages with:")
        print("   python -m pip install streamlit pandas requests python-dotenv")
        return False
    
    return True

def check_environment():
    """Check if environment variables are set"""
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv(env_path)
        else:
            print("⚠️ .env file not found in project root")
    except ImportError:
        print("⚠️ python-dotenv not installed, skipping .env file loading")

    required_env_vars = ['PAGE_ID', 'PAGE_ACCESS_TOKEN']
    missing_vars = []

    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("⚠️ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Make sure your .env file contains these variables")
        return False

    return True

def check_model():
    """Check if model files exist"""
    model_path = Path("src/models")

    if not model_path.exists():
        print("❌ Model directory not found: src/models")
        return False
    
    required_files = [
        "config.json",
        "model.safetensors",
        "tokenizer_config.json",
        "vocab.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not (model_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing model files:")
        for file in missing_files:
            print(f"   - src/models/{file}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🛡️ Starting Judol Remover Streamlit Application")
    print("=" * 50)
    
    # Check requirements
    print("📦 Checking requirements...")
    if not check_requirements():
        sys.exit(1)
    print("✅ All required packages are installed")
    
    # Check environment
    print("\n🔧 Checking environment...")
    if not check_environment():
        print("⚠️ Some environment variables are missing, but continuing...")
    else:
        print("✅ Environment variables are set")
    
    # Check model
    print("\n🤖 Checking model files...")
    if not check_model():
        print("⚠️ Model files missing, but continuing...")
    else:
        print("✅ Model files found")
    
    # Start Streamlit
    print("\n🚀 Starting Streamlit application...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("=" * 50)
    
    try:
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "src/app/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
