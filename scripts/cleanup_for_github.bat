@echo off
echo 🧹 Cleaning up project for GitHub upload...

REM Remove Node modules (largest space saver)
echo 📦 Removing Node modules...
if exist "frontend\node_modules" rmdir /s /q "frontend\node_modules"

REM Remove Python cache
echo 🐍 Removing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul

REM Remove virtual environments
echo 🔧 Removing virtual environments...
if exist "venv" rmdir /s /q "venv"
if exist ".venv" rmdir /s /q ".venv"
if exist "env" rmdir /s /q "env"
if exist "ENV" rmdir /s /q "ENV"

REM Remove generated reports
echo 📊 Removing generated reports...
del /q "performance_reports\*.html" 2>nul
del /q "performance_reports\*.json" 2>nul
del /q "performance_reports\*.csv" 2>nul
del /q "performance_reports\*.pdf" 2>nul
del /q "performance_reports\*.xlsx" 2>nul

REM Remove IDE files
echo 💻 Removing IDE files...
if exist ".vscode" rmdir /s /q ".vscode"
if exist ".idea" rmdir /s /q ".idea"
del /q *.swp 2>nul
del /q *.swo 2>nul

REM Remove OS files
echo 🖥️ Removing OS files...
del /s /q .DS_Store 2>nul
del /s /q Thumbs.db 2>nul

REM Remove log files
echo 📝 Removing log files...
del /s /q *.log 2>nul

REM Remove temporary files
echo 🗂️ Removing temporary files...
del /s /q *.tmp 2>nul
del /s /q *.temp 2>nul

echo ✅ Cleanup complete!
echo.
echo 🚀 Ready for GitHub upload!
