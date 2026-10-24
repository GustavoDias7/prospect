
@echo off
setlocal

set "ROOT=%~dp0"
set "PYTHON=%ROOT%..\venv\Scripts\pythonw.exe"
set "SCRIPT=%ROOT%..\scripts\launcher.py"

if not exist "%PYTHON%" (
    echo Error: Virtual environment Python not found.
    pause
    exit /b 1
)

if not exist "%SCRIPT%" (
    echo Error: launcher.py not found.
    pause
    exit /b 1
)

cd /d "%ROOT%"
start "" "%PYTHON%" "%SCRIPT%"

if errorlevel 1 (
    echo.
    echo The application exited with an error.
    pause
)

endlocal
