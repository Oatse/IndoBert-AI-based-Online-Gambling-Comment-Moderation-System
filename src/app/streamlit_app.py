#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Judol Remover - Streamlit Application (Refactored)
Aplikasi untuk mendeteksi dan menghapus komentar spam/judol dari Facebook menggunakan IndoBERT

This is the main entry point that uses the new modular architecture.
All functionality has been refactored into separate modules:
- ui_components.py: UI components and styling
- dashboard.py: Dashboard rendering
- pages/: Individual page modules
- app_controller.py: Main application controller
"""

# Import the new application controller with robust path handling
import sys
from pathlib import Path

# Add current directory and project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(project_root))

from app_controller import main

if __name__ == "__main__":
    main()