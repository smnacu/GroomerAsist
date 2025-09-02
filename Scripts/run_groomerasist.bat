@echo off
REM Simple launcher for GroomerAsist Kivy app
SETLOCAL
cd /d "%~dp0\..\mobile_app"
python main.py
ENDLOCAL