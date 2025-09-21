@echo off
echo 🌟 Premium Scraper Development Environment
echo ================================================

REM Check if we're in the right directory
if not exist "src" (
    echo ❌ Please run this script from the project root directory.
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Frontend directory not found. Please set up the frontend first.
    pause
    exit /b 1
)

if not exist ".env" (
    echo ⚠️  .env file not found. Please copy .env.example to .env and configure it.
    echo    copy .env.example .env
    pause
    exit /b 1
)

echo 🚀 Starting FastAPI backend server...
start "Backend Server" cmd /k "python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo 🎨 Starting Next.js frontend server...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo ✅ Both servers are starting up!
echo 📊 Backend API: http://localhost:8000
echo 📊 API Docs: http://localhost:8000/docs
echo 🎨 Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
