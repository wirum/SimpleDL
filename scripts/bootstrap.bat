@echo off
setlocal enabledelayedexpansion

echo ================================
echo SimpleDL Bootstrap (Windows)
echo ================================

:: Detect Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    where winget >nul 2>&1
    if %errorlevel% equ 0 (
        echo Python not found. Installing via winget...
        winget install Python.Python.3
    ) else (
        echo Python not found and winget not available.
        echo Please install manually:
        echo https://www.python.org/downloads/
        pause
        exit /b 1
    )
)
echo [STEP 1] Python OK

:: Go to project root (folder of this script)
cd /d %~dp0..

:: Create venv
if not exist .venv (
    echo [STEP 2] Creating virtual environment...
    %PYTHON% -m venv .venv
)

echo [STEP 3] Activating venv...
call .venv\Scripts\activate

:: Upgrade pip
echo [STEP 4] Upgrading pip...
python -m pip install --upgrade pip

if errorlevel 1 (
    echo [ERROR] pip upgrade failed
    exit /b 1
)

:: Install requirements
echo [STEP 5] Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed installing requirements
    exit /b 1
)

:: Check ffmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg not found in PATH
)

:: Check yt-dlp
python -c "import yt_dlp" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] yt-dlp not installed correctly
)

echo.
echo Bootstrap complete.
echo Run: python src/main.py
pause