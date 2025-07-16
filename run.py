#!/usr/bin/env python3
"""
Main entry point for Judol Remover Application
Runs the startup script from the scripts folder
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run the application startup script"""
    # Get the directory where this script is located (project root)
    project_root = Path(__file__).parent
    
    # Path to the startup script
    startup_script = project_root / "scripts" / "run_streamlit.py"
    
    if not startup_script.exists():
        print(f"❌ Startup script not found: {startup_script}")
        sys.exit(1)
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Run the startup script
    try:
        subprocess.run([sys.executable, str(startup_script)], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
