@echo off
echo Starting Amazon Scraper...
wsl -d Ubuntu-24.04 -e bash -c "cd ~/projects/kimm_coder/amazon && source venv/bin/activate && python3 scraper.py"

echo.
echo Scraping complete! Starting dashboard...
echo.

:: Start the dashboard dev server in the background
start /b wsl -d Ubuntu-24.04 -e bash -c "cd ~/projects/kimm_coder/amazon/dashboard && npm run dev"

:: Wait for the server to start
timeout /t 3 /nobreak >nul

:: Open browser to dashboard
start http://localhost:5173

echo Dashboard is running at http://localhost:5173
echo Press any key to stop the server and exit...
pause >nul

:: Kill the npm process
taskkill /f /im node.exe >nul 2>&1
