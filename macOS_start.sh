#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
BACKEND_VENV="$BACKEND_DIR/venv"
BACKEND_PORT=8000
FRONTEND_PORT=3000


BACKEND_PID=""
FRONTEND_PID=""

# --- Function to gracefully stop processes ---
# This function is called when the script receives an interrupt signal (e.g., CTRL+C).
cleanup() {
    echo -e "\nStopping backend and frontend servers..."

    
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID"
        echo "Backend (PID $BACKEND_PID) stopped."
    fi


    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID"
        echo "Frontend (PID $FRONTEND_PID) stopped."
    fi
    exit 0 
}

# Trap CTRL+C (SIGINT signal) to call the cleanup function
trap cleanup SIGINT

# --- Start Backend ---
echo "Starting backend server..."

cd "$BACKEND_DIR" || { echo "Error: Backend directory '$BACKEND_DIR' not found! Please ensure it exists."; exit 1; }

source "venv/bin/activate" || { echo "Error: Backend virtual environment not found or failed to activate! Run the setup script first."; exit 1; }

uvicorn main:app --port "$BACKEND_PORT" --reload &
BACKEND_PID=$! 
echo "Backend started with PID: $BACKEND_PID on http://localhost:$BACKEND_PORT"

deactivate

cd .. 

# --- Start Frontend ---
echo "Starting frontend server..."

cd "$FRONTEND_DIR" || { echo "Error: Frontend directory '$FRONTEND_DIR' not found! Please ensure it exists."; exit 1; }

npm start &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID on http://localhost:$FRONTEND_PORT"

cd ..

echo -e "\n----------------------------------------------------"
echo "Both backend and frontend servers are running! ✨"
echo "Backend: http://localhost:$BACKEND_PORT"
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "Press CTRL+C to stop both servers gracefully."
echo "----------------------------------------------------"

# Wait for both background processes to finish.
# This keeps the main script running until CTRL+C is pressed, allowing the cleanup function to be called.
wait "$BACKEND_PID" "$FRONTEND_PID"