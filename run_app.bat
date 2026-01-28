@echo off
setlocal
echo 🌿 Leaf Disease Detection System
echo --------------------------------

:: Step 1: Cleanup existing processes
echo 🧹 Cleaning up old processes...
taskkill /F /IM streamlit.exe /T 2>nul

:: Step 2: Install dependencies (optional, but good for first run)
echo 📦 Verifying dependencies...
pip install -r requirements.txt

:: Step 3: Start Streamlit App
echo 🚀 Launching App (Local Port 8502)...
streamlit run main.py --server.port 8502 --browser.gatherUsageStats false

pause
