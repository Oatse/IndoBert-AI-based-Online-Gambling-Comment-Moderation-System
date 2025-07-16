@echo off
echo Starting Infinite Loop Test...
echo Test will be available at: http://localhost:8502
echo.
python -m streamlit run scripts/test_infinite_loop.py --server.port 8502 --server.address localhost --browser.gatherUsageStats false
pause
