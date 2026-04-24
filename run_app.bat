@echo off
setlocal
title Emerald ITR Pro (AY 2026-27)

echo ================================================================================
echo EMERALD ITR PRO - Tax Year 2025-26 (AY 2026-27)
echo ================================================================================
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.10+ to run this application.
    pause
    exit /b 1
)

echo Launching Advanced Tax Engine...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo Application terminated with an error. 
    pause
)

endlocal
exit /b 0
