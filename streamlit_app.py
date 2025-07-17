#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Judol Remover - Streamlit Cloud Entry Point
Main entry point for Streamlit Cloud deployment
"""

import os
import sys
import streamlit as st
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """Setup environment for Streamlit Cloud deployment"""
    # Load secrets from Streamlit Cloud or environment variables
    if hasattr(st, 'secrets') and st.secrets:
        # Running on Streamlit Cloud - use secrets
        try:
            for key, value in st.secrets.items():
                if isinstance(value, str):
                    os.environ[key] = value
            st.success("✅ Loaded configuration from Streamlit Cloud secrets")
        except Exception as e:
            st.warning(f"⚠️ Error loading Streamlit secrets: {str(e)}")

    # Always try to load from .env as fallback (for local development)
    try:
        from dotenv import load_dotenv
        env_path = project_root / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            st.success("✅ Loaded configuration from .env file")
        else:
            st.info("ℹ️ No .env file found - using environment variables or Streamlit secrets")
    except ImportError:
        st.warning("⚠️ python-dotenv not installed. Using environment variables only.")

    # Validate required environment variables
    required_vars = ['PAGE_ID', 'PAGE_ACCESS_TOKEN']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        st.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        st.error("Please configure these in your .env file or Streamlit Cloud secrets.")
        return False

    return True

def check_model_files():
    """Check if model files exist, show warning if missing"""
    model_path = project_root / "src" / "models"
    
    if not model_path.exists():
        st.warning("⚠️ Model directory not found. Some features may not work properly.")
        return False
    
    required_files = ["config.json", "model.safetensors", "tokenizer_config.json", "vocab.txt"]
    missing_files = []
    
    for file in required_files:
        if not (model_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        st.warning(f"⚠️ Missing model files: {', '.join(missing_files)}. Spam detection may not work properly.")
        return False
    
    return True

def main():
    """Main application entry point for Streamlit Cloud"""
    st.set_page_config(
        page_title="Judol Remover",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Setup environment
    if not setup_environment():
        st.stop()

    # Check model files (non-blocking)
    check_model_files()

    # Import and run the main application
    try:
        from src.app.app_controller import main as app_main
        app_main()
    except ImportError as e:
        st.error(f"❌ Error importing application: {str(e)}")
        st.error("Please make sure all dependencies are installed and the project structure is correct.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error running application: {str(e)}")
        st.exception(e)
        st.stop()

if __name__ == "__main__":
    main()

