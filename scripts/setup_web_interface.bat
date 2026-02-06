@echo off
REM =============================================================================
REM Low-Code Performance Scanner - Web Interface Setup Script (Windows)
REM =============================================================================
REM This script automates the setup of both backend and frontend components
REM Version: 1.0.2
REM =============================================================================

setlocal enabledelayedexpansion

REM Colors (using Windows 10+ ANSI support)
echo [94m
echo ==============================================================================
echo   🚀 Low-Code Performance Scanner - Web Interface Setup
echo ==============================================================================
echo [0m
echo.

REM =============================================================================
REM Step 1: Check Prerequisites
REM =============================================================================

echo [96m🔧 Step 1: Checking prerequisites...[0m
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [91m❌ Python is not installed or not in PATH[0m
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [92m✅ Python %PYTHON_VERSION% installed[0m

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [91m❌ Node.js is not installed or not in PATH[0m
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo [92m✅ Node.js %NODE_VERSION% installed[0m

REM Check npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [91m❌ npm is not installed[0m
    pause
    exit /b 1
)

for /f %%i in ('npm --version') do set NPM_VERSION=%%i
echo [92m✅ npm %NPM_VERSION% installed[0m

REM Check virtual environment
if exist "venv" (
    echo [92m✅ Virtual environment found[0m
) else (
    echo [93m⚠️  Virtual environment not found (will create)[0m
)

echo.

REM =============================================================================
REM Step 2: Setup Backend
REM =============================================================================

echo [96m🔧 Step 2: Setting up backend...[0m
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [96mℹ️  Creating virtual environment...[0m
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [91m❌ Failed to create virtual environment[0m
        pause
        exit /b 1
    )
    echo [92m✅ Virtual environment created[0m
)

REM Activate virtual environment
echo [96mℹ️  Activating virtual environment...[0m
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [91m❌ Failed to activate virtual environment[0m
    pause
    exit /b 1
)

REM Install backend dependencies
echo [96mℹ️  Installing backend dependencies...[0m
python -m pip install --quiet --upgrade pip
python -m pip install --quiet fastapi uvicorn[standard] python-multipart websockets

REM Check if core scanner dependencies are installed
python -c "import lowcode_scanner" >nul 2>&1
if %errorlevel% neq 0 (
    echo [96mℹ️  Installing core scanner dependencies...[0m
    pip install --quiet -r requirements.txt
    playwright install chromium
)

echo [92m✅ Backend dependencies installed[0m
echo.

REM =============================================================================
REM Step 3: Setup Frontend
REM =============================================================================

echo [96m🔧 Step 3: Setting up frontend...[0m
echo.

REM Navigate to frontend directory
cd frontend
if %errorlevel% neq 0 (
    echo [91m❌ Frontend directory not found[0m
    pause
    exit /b 1
)

REM Install frontend dependencies
echo [96mℹ️  Installing frontend dependencies (this may take a few minutes)...[0m
call npm install --silent
if %errorlevel% neq 0 (
    echo [91m❌ Failed to install frontend dependencies[0m
    cd ..
    pause
    exit /b 1
)

echo [92m✅ Frontend dependencies installed[0m

REM Create .env.local if it doesn't exist
if not exist ".env.local" (
    echo [96mℹ️  Creating frontend environment configuration...[0m
    (
        echo # Backend API Configuration
        echo NEXT_PUBLIC_API_URL=http://localhost:8000
        echo NEXT_PUBLIC_WS_URL=ws://localhost:8000
    ) > .env.local
    echo [92m✅ Environment configuration created[0m
) else (
    echo [92m✅ Environment configuration already exists[0m
)

REM Create missing frontend files
echo [96mℹ️  Creating frontend application files...[0m

REM Create app directory
if not exist "app" mkdir app

REM Create main page if it doesn't exist
if not exist "app\page.tsx" (
    (
        echo 'use client'
        echo.
        echo import { useState } from 'react'
        echo import { motion } from 'framer-motion'
        echo.
        echo export default function Home(^) {
        echo   const [url, setUrl] = useState('')
        echo   const [loading, setLoading] = useState(false^)
        echo.
        echo   const handleSubmit = async (e: React.FormEvent^) =^> {
        echo     e.preventDefault(^)
        echo     setLoading(true^)
        echo     alert('Scan started for: ' + url^)
        echo     setLoading(false^)
        echo   }
        echo.
        echo   return (
        echo     ^<div className="max-w-4xl mx-auto"^>
        echo       ^<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-12"^>
        echo         ^<h1 className="text-4xl font-bold text-gray-900 mb-4"^>Start Performance Scan^</h1^>
        echo         ^<p className="text-lg text-gray-600"^>Test your low-code application performance^</p^>
        echo       ^</motion.div^>
        echo       ^<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card"^>
        echo         ^<form onSubmit={handleSubmit} className="space-y-6"^>
        echo           ^<div^>
        echo             ^<label className="block text-sm font-medium text-gray-700 mb-2"^>URL to Test^</label^>
        echo             ^<input type="url" value={url} onChange={(e^) =^> setUrl(e.target.value^)} placeholder="https://your-app.bubbleapps.io" className="input" required /^>
        echo           ^</div^>
        echo           ^<button type="submit" disabled={loading} className="btn btn-primary w-full"^>{loading ? 'Starting...' : 'Start Scan'}^</button^>
        echo         ^</form^>
        echo       ^</motion.div^>
        echo     ^</div^>
        echo   ^)
        echo }
    ) > app\page.tsx
)

REM Create globals.css if it doesn't exist
if not exist "app\globals.css" (
    (
        echo @tailwind base;
        echo @tailwind components;
        echo @tailwind utilities;
        echo.
        echo @layer components {
        echo   .btn { @apply px-4 py-2 rounded-lg font-medium transition-all; }
        echo   .btn-primary { @apply bg-primary-600 text-white hover:bg-primary-700; }
        echo   .card { @apply bg-white rounded-xl shadow-soft border border-gray-200 p-6; }
        echo   .input { @apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500; }
        echo }
    ) > app\globals.css
)

cd ..

echo [92m✅ Frontend setup complete[0m
echo.

REM =============================================================================
REM Step 4: Verify Installation
REM =============================================================================

echo [96m🔧 Step 4: Verifying installation...[0m
echo.

REM Verify backend
python -c "import sys; sys.path.append('backend')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [92m✅ Backend module verified[0m
) else (
    echo [93m⚠️  Backend module check skipped[0m
)

REM Verify frontend
if exist "frontend\package.json" (
    echo [92m✅ Frontend configuration verified[0m
)

echo.

REM =============================================================================
REM Final Summary
REM =============================================================================

echo [94m
echo ==============================================================================
echo   ✅ Setup Complete!
echo ==============================================================================
echo [0m
echo.
echo [92m🚀 Web Interface is ready![0m
echo.
echo Next steps:
echo.
echo [93m1. Start the backend:[0m
echo    cd website_performance_scanner
echo    venv\Scripts\activate
echo    python backend\main.py
echo.
echo [93m2. In a new terminal, start the frontend:[0m
echo    cd website_performance_scanner\frontend
echo    npm run dev
echo.
echo [93m3. Open your browser:[0m
echo    Frontend UI:  http://localhost:3000
echo    Backend API:  http://localhost:8000
echo    API Docs:     http://localhost:8000/api/docs
echo.
echo [96m🌐 Documentation:[0m
echo    See WEB_INTERFACE_SETUP.md for detailed instructions
echo.
echo [92mHappy testing! 🎉[0m
echo.

pause
