@echo off
title DataSense.AI - Setup
echo ============================================
echo    DataSense.AI - Online Shopping Analysis
echo    Automated Setup Script
echo ============================================
echo.

:: Step 1 - Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Download from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
python --version
echo.

:: Step 2 - Create virtual environment
echo [2/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists, skipping.
)
echo.

:: Step 3 - Activate venv and install dependencies
echo [3/5] Installing dependencies (this may take a few minutes)...
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo.

:: Step 4 - Create .env file
echo [4/5] Configuring environment...
if not exist ".env" (
    copy .env.example .env
    echo.
    echo ============================================
    echo  IMPORTANT: Edit the .env file now!
    echo  Set your MySQL password and other settings.
    echo ============================================
    echo.
    notepad .env
) else (
    echo .env file already exists, skipping.
)
echo.

:: Step 5 - Database setup reminder
echo [5/5] Database Setup...
echo.
echo  You need to set up MySQL manually:
echo    1. Open MySQL (Workbench or command line)
echo    2. Run:  mysql -u root -p ^< schema.sql
echo    OR open schema.sql in MySQL Workbench and execute it.
echo.
echo ============================================
echo  Setup Complete!
echo  To run the app:
echo    1. Open a terminal in this folder
echo    2. Run:  venv\Scripts\activate
echo    3. Run:  python app.py
echo    4. Open:  http://127.0.0.1:5000
echo ============================================
echo.
pause
