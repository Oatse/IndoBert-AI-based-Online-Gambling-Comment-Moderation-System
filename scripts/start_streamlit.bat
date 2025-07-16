@echo off
echo 🛡️ Starting Judol Remover Streamlit Application
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📦 Installing/updating requirements...
pip install -r config/requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️ .env file not found
    echo Please create .env file with your Facebook credentials
    echo Example:
    echo PAGE_ID=your_page_id
    echo PAGE_ACCESS_TOKEN=your_access_token
    pause
)

REM Start the application
echo 🚀 Starting Streamlit application...
python run_streamlit.py

pause
