@echo off
setlocal enabledelayedexpansion

:: Set window title
title QuizForge Launcher

:: Define colors for better UI - use PowerShell-compatible format
set "ESC="
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
  set "ESC=%%b"
)

set "BLUE=%ESC%[36m"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "RED=%ESC%[31m"
set "RESET=%ESC%[0m"

:: ==========================================
:: Main Menu
:: ==========================================
:MAIN_MENU
cls
echo %BLUE%=============================================%RESET%
echo %BLUE%            QuizForge Launcher              %RESET%
echo %BLUE%=============================================%RESET%
echo.
echo Choose an option:
echo %GREEN%1.%RESET% Start both frontend and backend
echo %GREEN%2.%RESET% Start backend only
echo %GREEN%3.%RESET% Start frontend only
echo %GREEN%4.%RESET% Install dependencies
echo %GREEN%5.%RESET% Update dependencies
echo %GREEN%6.%RESET% Run tests
echo %GREEN%7.%RESET% Clean up (stop all servers)
echo %GREEN%8.%RESET% Clean caches
echo %GREEN%0.%RESET% Exit
echo.

set /p choice="Enter your choice (0-8): "

if "%choice%"=="1" goto START_ALL
if "%choice%"=="2" goto START_BACKEND
if "%choice%"=="3" goto START_FRONTEND
if "%choice%"=="4" goto INSTALL_DEPS
if "%choice%"=="5" goto UPDATE_DEPS
if "%choice%"=="6" goto RUN_TESTS
if "%choice%"=="7" goto CLEANUP
if "%choice%"=="8" goto CLEAN_CACHE
if "%choice%"=="0" goto END

echo %RED%Invalid choice. Please try again.%RESET%
timeout /t 2 >nul
goto MAIN_MENU

:: ==========================================
:: Helper Functions
:: ==========================================
:CHECK_PYTHON
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %RED%Python is not installed or not in PATH. Please install Python and try again.%RESET%
    pause
    goto MAIN_MENU
)
goto :EOF

:CREATE_DIRS
if not exist backend\uploads mkdir backend\uploads
goto :EOF

:SETUP_VENV
cd backend
if not exist venv (
    echo %YELLOW%Creating virtual environment...%RESET%
    python -m venv venv
)
call venv\Scripts\activate.bat
echo %YELLOW%Installing backend dependencies...%RESET%
pip install -r requirements.txt
call venv\Scripts\deactivate.bat
cd ..
goto :EOF

:SETUP_FRONTEND
cd frontend
if not exist node_modules (
    echo %YELLOW%Installing frontend dependencies...%RESET%
    npm install
)
cd ..
goto :EOF

:KILL_SERVERS
echo %YELLOW%Stopping any existing processes...%RESET%
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
goto :EOF

:: ==========================================
:: Main Actions
:: ==========================================
:START_ALL
call :KILL_SERVERS
call :CHECK_PYTHON
call :CREATE_DIRS
call :SETUP_VENV
call :SETUP_FRONTEND

echo %GREEN%Starting backend server...%RESET%
start cmd /k "cd backend && call venv\Scripts\activate.bat && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

echo %YELLOW%Waiting for backend to initialize...%RESET%
timeout /t 12 /nobreak > nul

echo %GREEN%Starting frontend server...%RESET%
start cmd /k "cd frontend && npm run dev"

echo.
echo %GREEN%QuizForge is starting!%RESET%
echo.
echo Backend server: http://localhost:8000
echo Frontend server: http://localhost:3000
echo.
echo %YELLOW%Note: Backend may take a few moments to fully initialize.%RESET%
echo %YELLOW%The frontend will automatically detect when the backend is available.%RESET%
echo.
echo %YELLOW%Press any key to return to the main menu...%RESET%
pause > nul
goto MAIN_MENU

:START_BACKEND
call :KILL_SERVERS
call :CHECK_PYTHON
call :CREATE_DIRS
call :SETUP_VENV

echo %GREEN%Starting backend server...%RESET%
start cmd /k "cd backend && call venv\Scripts\activate.bat && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

echo %YELLOW%Waiting for backend to initialize...%RESET%
timeout /t 10 /nobreak > nul

echo.
echo %GREEN%Backend server should be running at: http://localhost:8000%RESET%
echo.
echo %YELLOW%Press any key to return to the main menu...%RESET%
pause > nul
goto MAIN_MENU

:START_FRONTEND
call :KILL_SERVERS
call :SETUP_FRONTEND

echo %GREEN%Starting frontend server...%RESET%
start cmd /k "cd frontend && npm run dev"

echo.
echo %GREEN%Frontend server should be running at: http://localhost:3000%RESET%
echo.
echo %YELLOW%Press any key to return to the main menu...%RESET%
pause > nul
goto MAIN_MENU

:INSTALL_DEPS
call :CHECK_PYTHON
call :SETUP_VENV
call :SETUP_FRONTEND

echo.
echo %GREEN%All dependencies have been installed.%RESET%
echo.
echo %YELLOW%Press any key to return to the main menu...%RESET%
pause > nul
goto MAIN_MENU

:UPDATE_DEPS
call :CHECK_PYTHON

echo %YELLOW%Updating backend dependencies...%RESET%
cd backend
call venv\Scripts\activate.bat
pip install --upgrade -r requirements.txt
call venv\Scripts\deactivate.bat
cd ..

echo %YELLOW%Updating frontend dependencies...%RESET%
cd frontend
npm update
cd ..

echo.
echo %GREEN%All dependencies have been updated.%RESET%
echo.
echo %YELLOW%Press any key to return to the main menu...%RESET%
pause > nul
goto MAIN_MENU

:RUN_TESTS
call :CHECK_PYTHON

echo %YELLOW%Running backend tests...%RESET%
cd backend
call venv\Scripts\activate.bat
python test_api_connection.py
set "TEST_STATUS=%ERRORLEVEL%"
call venv\Scripts\deactivate.bat
cd ..

if "%TEST_STATUS%"=="0" (
    echo %GREEN%✅ Backend tests passed!%RESET%
) else (
    echo %RED%❌ Backend tests failed.%RESET%
    echo %YELLOW%Make sure the backend server is running.%RESET%
)

echo.
echo %YELLOW%Press any key to return to the main menu...%RESET%
pause > nul
goto MAIN_MENU

:CLEANUP
call :KILL_SERVERS
echo %GREEN%All servers have been stopped.%RESET%
echo.
echo %YELLOW%Press any key to return to the main menu...%RESET%
pause > nul
goto MAIN_MENU

:CLEAN_CACHE
echo %YELLOW%Cleaning caches...%RESET%

:: Clean frontend cache
echo %YELLOW%Cleaning frontend cache...%RESET%
cd frontend
if exist .next (
    echo %YELLOW%Removing Next.js build cache...%RESET%
    rmdir /s /q .next
)
if exist node_modules\.cache (
    echo %YELLOW%Removing npm cache...%RESET%
    rmdir /s /q node_modules\.cache
)
cd ..

:: Clean backend cache
echo %YELLOW%Cleaning backend cache...%RESET%
cd backend
if exist __pycache__ (
    echo %YELLOW%Removing Python cache...%RESET%
    rmdir /s /q __pycache__
)
if exist app\__pycache__ (
    echo %YELLOW%Removing app Python cache...%RESET%
    rmdir /s /q app\__pycache__
)
if exist app\api\__pycache__ (
    echo %YELLOW%Removing API Python cache...%RESET%
    rmdir /s /q app\api\__pycache__
)
cd ..

echo.
echo %GREEN%Cache cleaning completed!%RESET%
echo.
echo %YELLOW%Press any key to return to the main menu...%RESET%
pause > nul
goto MAIN_MENU

:END
call :KILL_SERVERS
echo %GREEN%Thank you for using QuizForge!%RESET%
endlocal
exit /b 0 