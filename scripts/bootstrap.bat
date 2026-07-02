@echo off
REM SimpleDL bootstrap (Windows)
SETLOCAL ENABLEDELAYEDEXPANSION

echo SimpleDL bootstrap (Windows)

where python >nul 2>&1
if errorlevel 1 (
  echo Error: Python not found on PATH. Install Python 3 and re-run this script.
  pause
  exit /b 1
)

set USE_VENV=
echo.
set /p USE_VENV="Create and use a virtualenv? [Y/n]: "
if "%USE_VENV%"==" " set USE_VENV=Y
if /I "%USE_VENV%"=="" set USE_VENV=Y

if /I "%USE_VENV%"=="N" goto globalinst
if /I "%USE_VENV%"=="n" goto globalinst

REM Use venv
echo.
echo Creating virtualenv .venv...
python -m venv .venv
if errorlevel 1 (
  echo Error creating virtualenv
  pause
  exit /b 1
)

echo Activating virtualenv and installing requirements...
call .venv\Scripts\activate.bat
if errorlevel 1 (
  echo Error activating virtualenv
  pause
  exit /b 1
)

python -m pip install -U pip
pip install -r requirements.txt
goto checks

:globalinst
echo.
echo Installing requirements globally (you may need admin privileges)...
python -m pip install -U pip
pip install -r requirements.txt

:checks
echo.
echo Basic checks:
where ffmpeg >nul 2>&1
if errorlevel 1 (
  echo Warning: ffmpeg not found. Post-processing (audio extraction/embedding) may fail.
) else (
  echo ffmpeg: OK
)

echo.
echo See config.example.yml to create config.yml with custom options.
echo Bootstrap complete!
pause
ENDLOCAL
