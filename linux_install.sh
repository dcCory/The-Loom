#!/bin/bash

set -e

REQUIREMENTS_FILE=""

# --- User Input ---
echo "Which device type will you be using?"
echo "1) CPU"
echo "2) NVIDIA GPU"
echo "3) AMD GPU"
read -p "Enter your choice (1, 2, or 3): " CHOICE


case "$CHOICE" in
    1)
        echo "You chose CPU. Installing CPU-only dependencies."
        export CMAKE_ARGS=""
        export FORCE_CMAKE=1
        REQUIREMENTS_FILE="requirements-cpu.txt"
        ;;
    2)
        echo "You chose NVIDIA GPU. Setting up for CUDA compilation."
        export CMAKE_ARGS="-DLLAMA_CUBLAS=on"
        export FORCE_CMAKE=1
        REQUIREMENTS_FILE="requirements-cuda.txt"
        ;;
    3)
        echo "You chose AMD GPU. Setting up for ROCm compilation."
        export CMAKE_ARGS="-DLLAMA_HIPBLAS=on"
        export FORCE_CMAKE=1
        REQUIREMENTS_FILE="requirements-rocm.txt"
        ;;
    *)
        echo "Invalid choice. Please run the script again and choose 1, 2, or 3."
        exit 1
        ;;
esac


if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "Error: The selected requirements file '$REQUIREMENTS_FILE' does not exist."
    echo "Please ensure you have 'requirements-cpu.txt', 'requirements-cuda.txt', and 'requirements-rocm.txt' in the same directory."
    exit 1
fi

# --- Main Installation Steps ---
# Remove existing venv directory if it exists
if [ -d "backend/venv" ]; then
    echo "Existing virtual environment found at 'backend/venv'."
    read -p "Do you want to remove it for a fresh install? (y/n): " REMOVE_CHOICE
    if [[ "$REMOVE_CHOICE" =~ ^[Yy]$ ]]; then
        echo "Removing 'backend/venv'..."
        rm -rf "vackend/venv"
    else
        echo "Skipping removal. Re-installing dependencies in the existing environment."
    fi
fi

# Create parent directory if it doesn't exist

echo "Creating a Python virtual environment at 'backend/venv'..."
python3 -m venv "backend/venv"

echo "Activating the virtual environment..."
source "backend/venv/bin/activate"

echo "Installing dependencies from '$REQUIREMENTS_FILE'..."
pip install -r "$REQUIREMENTS_FILE"

echo "Deactivating the virtual environment..."
deactivate

echo "Installation complete! 🎉"
echo "To use your environment, run: source $VENV_PATH/bin/activate"
echo "Then you can run your Python scripts."
