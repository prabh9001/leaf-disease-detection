@echo off
setlocal
echo 🌿 Leaf Disease Detection System
echo --------------------------------

:: Step 1: Cleanup existing processes
echo 🧹 Cleaning up old processes...
taskkill /F /IM uvicorn.exe /T 2>nul
taskkill /F /IM streamlit.exe /T 2>nul

:: Step 2: Start FastAPI Backend
echo ⚙️  Starting Backend (Port 8001)...
start "Leaf-Backend" /min cmd /c "uvicorn app:app --port 8001"

:: Step 3: Wait and verify backend
echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

:: Step 4: Start Streamlit Frontend
echo 🚀 Launching Frontend (Port 8502)...
streamlit run main.py --server.port 8502

pause
