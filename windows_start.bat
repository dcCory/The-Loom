@echo off

setlocal enableDelayedExpansion

REM --- Configuration ---
set "BACKEND_DIR=backend"
set "FRONTEND_DIR=frontend"

set "BACKEND_VENV_ACTIVATE_SCRIPT=%BACKEND_DIR%\venv\Scripts\activate.bat"
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=3000"

REM --- Cleanup Function ---

:cleanup
    echo.
    echo Stopping backend and frontend servers...


    taskkill /IM python.exe /FI "WINDOWTITLE eq Backend Server" /F >NUL 2>&1

    if !errorlevel! equ 0 (
        echo Backend (uvicorn in 'Backend Server' window) stopped.
    ) else (
        echo Backend (uvicorn in 'Backend Server' window) not found or failed to stop.
    )


    taskkill /IM node.exe /FI "WINDOWTITLE eq Frontend Server" /F >NUL 2>&1
    if !errorlevel! equ 0 (
        echo Frontend (npm in 'Frontend Server' window) stopped.
    ) else (
        echo Frontend (npm in 'Frontend Server' window) not found or failed to stop.
    )

    exit /b 0

REM --- Start Backend Server ---
echo Starting backend server...

if not exist "%BACKEND_DIR%\" (
    echo Error: Backend directory '%BACKEND_DIR%' not found!
    exit /b 1
)

cd "%BACKEND_DIR%" || (
    echo Error: Failed to change to backend directory!
    exit /b 1
)

if not exist "%BACKEND_VENV_ACTIVATE_SCRIPT%" (
    echo Error: Backend virtual environment activation script not found at '%BACKEND_VENV_ACTIVATE_SCRIPT%'!
    cd ..
    exit /b 1
)

echo Launching: start "Backend Server" cmd /k ""call "%BACKEND_VENV_ACTIVATE_SCRIPT%" && uvicorn main:app --port %BACKEND_PORT% --reload""
start "Backend Server" cmd /k ""call "%BACKEND_VENV_ACTIVATE_SCRIPT%" && uvicorn main:app --port %BACKEND_PORT% --reload""
if !errorlevel! neq 0 (
    echo Error: Failed to launch backend server.
    cd ..
    exit /b 1
)
echo Backend server launched in a new window on http://localhost:%BACKEND_PORT%


cd .. || (
    echo Error: Failed to return to root directory after backend start!
    goto :cleanup
)

REM --- Start Frontend Server ---
echo Starting frontend server...

if not exist "%FRONTEND_DIR%\" (
    echo Error: Frontend directory '%FRONTEND_DIR%' not found!
    goto :cleanup
)
REM
cd "%FRONTEND_DIR%" || (
    echo Error: Failed to change to frontend directory!
    goto :cleanup
)


echo Launching: start "Frontend Server" cmd /k ""npm start""
start "Frontend Server" cmd /k ""npm start""
if !errorlevel! neq 0 (
    echo Error: Failed to launch frontend server.
    cd ..
    goto :cleanup
)
echo Frontend server launched in a new window on http://localhost:%FRONTEND_PORT%


cd .. || (
    echo Error: Failed to return to root directory after frontend start!
    goto :cleanup
)

echo.
echo ----------------------------------------------------
echo Both backend and frontend servers are running! 🎉
echo Backend: http://localhost:%BACKEND_PORT%
echo Frontend: http://localhost:%FRONTEND_PORT%
echo.
echo Press CTRL+C in THIS window to stop both servers.
echo ----------------------------------------------------


timeout /t -1 /nobreak >NUL 2>&1

REM This line is reached when the TIMEOUT command is interrupted by CTRL+C.
goto :cleanup

endlocal