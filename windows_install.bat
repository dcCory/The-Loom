@echo off
REM 
setlocal enableDelayedExpansion

REM --- Initialize Variables ---
 
set "FRONTEND_DIR=frontend"
set "VENV_DIR=backend\venv"
set "REQUIREMENTS_FILE="

REM --- User Input for Device Type ---
echo Which device type will you be using?
echo 1) CPU
echo 2) NVIDIA GPU
echo 3) AMD GPU

:get_choice
 
set /p CHOICE="Enter your choice (1, 2, or 3): "

 
if "%CHOICE%"=="1" (
    echo You chose CPU. Installing CPU-only dependencies.
     
    set "REQUIREMENTS_FILE=backend\requirements-cpu.txt"
) else if "%CHOICE%"=="2" (
    echo You chose NVIDIA GPU. Setting up for CUDA compilation.
     
    set "REQUIREMENTS_FILE=backend\requirements-cuda.txt"
) else if "%CHOICE%"=="3" (
    echo You chose AMD GPU. Setting up for ROCm compilation.
     
    set "REQUIREMENTS_FILE=backend\requirements-rocm.txt"
) else (
     
    echo Invalid choice. Please enter 1, 2, or 3.
    goto :get_choice
)

REM --- Validate Requirements File Exists ---
 
if not exist "%REQUIREMENTS_FILE%" (
    echo Error: The selected requirements file '%REQUIREMENTS_FILE%' does not exist.
    echo Please ensure you have 'requirements-cpu.txt', 'requirements-cuda.txt', and 'requirements-rocm.txt' in the 'backend' directory.
    exit /b 1
)

REM --- Main Python Installation Steps ---


if exist "%VENV_DIR%\" (
    echo Existing virtual environment found at '%VENV_DIR%'.
    set /p REMOVE_CHOICE="Do you want to remove it for a fresh install? (y/n): "
     
    if /i "%REMOVE_CHOICE%"=="y" (
        echo Removing '%VENV_DIR%'...
         
        rmdir /s /q "%VENV_DIR%"
         
        if exist "%VENV_DIR%\" (
            echo Error: Failed to remove virtual environment. Please check permissions or ensure no files are in use.
            exit /b 1
        )
    ) else (
        echo Skipping removal. Re-installing dependencies in the existing environment.
    )
)


if not exist "backend\" (
    mkdir backend
    if %errorlevel% neq 0 (
        echo Error: Failed to create 'backend' directory.
        exit /b 1
    )
)

echo Creating a Python virtual environment at '%VENV_DIR%'...

python -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment. Make sure Python is installed and added to your system PATH.
    exit /b 1
)

echo Activating the virtual environment...

call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment.
    exit /b 1
)

echo Installing dependencies from '%REQUIREMENTS_FILE%'...
pip install -r "%REQUIREMENTS_FILE%"
if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies.
     
    call deactivate.bat
    exit /b 1
)

 
set "CMAKE_ARGS="
set "FORCE_CMAKE="

echo Deactivating the virtual environment...
call deactivate.bat
 
if %errorlevel% neq 0 (
    echo Warning: Failed to deactivate virtual environment cleanly.
)

REM --- Frontend Installation Steps ---
echo --- Setting up Frontend ---


if not exist "%FRONTEND_DIR%\" (
    echo Error: Frontend directory '%FRONTEND_DIR%' not found. Please ensure it exists.
    exit /b 1
)


cd "%FRONTEND_DIR%"
if %errorlevel% neq 0 (
    echo Error: Failed to change to frontend directory.
    exit /b 1
)

echo Installing Node.js dependencies for the frontend...
npm install
if %errorlevel% neq 0 (
    echo Error: Failed to install Node.js dependencies. Make sure Node.js and npm are installed and added to your system PATH.
    cd ..
    exit /b 1
)

echo Building the frontend for production...
npm run build
if %errorlevel% neq 0 (
    echo Error: Failed to build frontend.
    cd ..
    exit /b 1
)

echo Returning to project root directory...
cd ..

REM --- Installation Complete ---
echo.
echo Installation complete! 🎉
echo Welcome to The Loom! Check out the README and user_manual to get started!

REM End delayed expansion and exit the script successfully
endlocal
exit /b 0