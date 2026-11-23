@echo off
setlocal

REM ===== Config =====
set SCRIPT=main.py
set EXENAME=main
REM ==================

REM Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Check the target script exists
if not exist "%SCRIPT%" (
    echo Could not find %SCRIPT% in this folder.
    pause
    exit /b 1
)

REM Install PyInstaller if missing
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install --upgrade pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

REM Build the exe
echo Building %EXENAME%.exe ...
python -m PyInstaller --onefile --noconsole --name "%EXENAME%" "%SCRIPT%"

if errorlevel 1 (
    echo.
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Done. Your exe is in the "dist" folder: dist\%EXENAME%.exe
pause