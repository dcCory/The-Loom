#!/bin/bash

set -e

REQUIREMENTS_FILE=""

# --- User Input & Device Type Selection ---
echo "--- Device Type Selection for macOS ---"
echo "This script is tailored for macOS environments."
echo ""
echo "Due to architectural differences, macOS does not directly support"
echo "NVIDIA's CUDA or AMD's ROCm platforms in the same way Linux or Windows do."
echo "Therefore, this script will proceed with a **CPU-only** backend setup"
echo "to ensure broad compatibility across all macOS systems (Intel and Apple Silicon)."
echo "Proceeding with CPU-only backend installation."
REQUIREMENTS_FILE="backend/requirements-cpu.txt"

# Verify the CPU requirements file exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "Error: The required file '$REQUIREMENTS_FILE' does not exist."
    echo "Please ensure you have 'requirements-cpu.txt' inside the 'backend/' directory."
    exit 1
fi

# --- Main Backend Installation Steps ---
echo ""
echo "--- Setting up Python Backend ---"


mkdir -p "backend"


if [ -d "backend/venv" ]; then
    echo "Existing Python virtual environment found at 'backend/venv'."
    read -p "Do you want to remove it for a fresh install? (y/n): " REMOVE_CHOICE
    if [[ "$REMOVE_CHOICE" =~ ^[Yy]$ ]]; then
        echo "Removing 'backend/venv'..."
        rm -rf "backend/venv"
    else
        echo "Skipping removal. Dependencies will be re-installed in the existing environment."
    fi
fi

echo "Creating a new Python virtual environment at 'backend/venv'..."

python3.12 -m venv "backend/venv"

echo "Activating the virtual environment..."
source "backend/venv/bin/activate"

echo "Installing CPU-only dependencies from '$REQUIREMENTS_FILE'..."
pip install -r "$REQUIREMENTS_FILE"

echo "Deactivating the virtual environment..."
deactivate

# --- Frontend Installation Steps ---
echo ""
echo "--- Setting up Frontend ---"
FRONTEND_DIR="frontend"


if [ ! -d "$FRONTEND_DIR" ]; then
    echo "Error: Frontend directory '$FRONTEND_DIR' not found."
    echo "Please ensure the 'frontend' directory exists in your project root."
    exit 1
fi


cd "$FRONTEND_DIR"

echo "Installing Node.js dependencies for the frontend..."
npm install

echo "Building the frontend for production..."
npm run build

# Return to the project root directory
echo "Returning to project root directory..."
cd ..

echo ""
echo "--- Installation Complete!  ---"
echo "Your backend (CPU-only) and frontend have been set up."
echo "Welcome to The Loom! Check out the README and user_manual to get started!"