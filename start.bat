@echo off
echo ====================================================================
echo Stock Market Analysis System - Startup
echo ====================================================================
echo.
echo Starting the system...
echo.

REM Activate virtual environment and run the unified startup script
call venv\Scripts\activate.bat
python start_system.py

pause
