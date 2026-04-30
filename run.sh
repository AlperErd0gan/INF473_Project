#!/bin/bash

# Add Homebrew and Node to PATH
export PATH="/opt/homebrew/bin:/opt/homebrew/opt/node@20/bin:$PATH"

echo "Starting the GSU Transcript Agent System..."

# Function to handle cleanup on script exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Start Backend
echo "--> Starting FastAPI Backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

python -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
deactivate
cd ..

# Start Frontend
echo "--> Starting React Frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "node_modules not found. Running npm install..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================================="
echo "System is running!"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173 (usually)"
echo "Press Ctrl+C to stop both servers."
echo "=========================================================="

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID
