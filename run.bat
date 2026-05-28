@echo off
title DataSense.AI - Runner
echo ============================================
echo    Starting DataSense.AI Workspace...
echo ============================================
echo.
if not exist "venv" (
    echo ERROR: Virtual environment 'venv' not found!
    echo Please run setup.bat first to configure the workspace.
    pause
    exit /b 1
)
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Starting Flask server...
python app.py
pause
