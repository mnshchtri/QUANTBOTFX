#!/bin/bash

# QuantBotForex Quick Start Script
# This script starts both backend and frontend services

set -e  # Exit on any error

echo "🚀 QuantBotForex Quick Start"
echo "============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if services are already running
check_running_services() {
    print_header "Checking running services..."
    
    # Check backend
    if lsof -i :8000 > /dev/null 2>&1; then
        print_warning "Backend already running on port 8000"
        BACKEND_RUNNING=true
    else
        print_status "Backend not running"
        BACKEND_RUNNING=false
    fi
    
    # Check frontend
    if lsof -i :3000 > /dev/null 2>&1; then
        print_warning "Frontend already running on port 3000"
        FRONTEND_RUNNING=true
    else
        print_status "Frontend not running"
        FRONTEND_RUNNING=false
    fi
}

# Start backend
start_backend() {
    if [ "$BACKEND_RUNNING" = true ]; then
        print_status "Backend already running, skipping..."
        return
    fi
    
    print_header "Starting Backend..."
    
    if [ ! -f "backend/app.py" ]; then
        print_error "Backend app.py not found. Please run setup.sh first."
        exit 1
    fi
    
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "../.venv" ]; then
        print_error "Virtual environment not found. Please run setup.sh first."
        exit 1
    fi
    
    print_status "Activating virtual environment..."
    source ../.venv/bin/activate
    
    print_status "Starting FastAPI backend on port 8000..."
    python app.py &
    BACKEND_PID=$!
    
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    # Check if backend started successfully
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "✅ Backend started successfully (PID: $BACKEND_PID)"
    else
        print_warning "Backend may still be starting up..."
    fi
}

# Start frontend
start_frontend() {
    if [ "$FRONTEND_RUNNING" = true ]; then
        print_status "Frontend already running, skipping..."
        return
    fi
    
    print_header "Starting Frontend..."
    
    if [ ! -f "frontend/package.json" ]; then
        print_error "Frontend package.json not found. Please run setup.sh first."
        exit 1
    fi
    
    cd frontend
    
    print_status "Starting React frontend on port 3000..."
    npm start &
    FRONTEND_PID=$!
    
    cd ..
    
    print_status "✅ Frontend started successfully (PID: $FRONTEND_PID)"
}

# Show service status
show_status() {
    print_header "Service Status"
    echo ""
    echo "Backend:  http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "To stop services:"
    echo "  pkill -f 'python app.py'  # Stop backend"
    echo "  pkill -f 'npm start'       # Stop frontend"
    echo ""
    echo "Press Ctrl+C to stop this script (services will continue running)"
}

# Cleanup function
cleanup() {
    echo ""
    print_warning "Stopping QuantBotForex services..."
    
    # Stop backend
    if [ ! -z "$BACKEND_PID" ]; then
        print_status "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    # Stop frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        print_status "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    print_status "Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main function
main() {
    print_header "Starting QuantBotForex services..."
    
    check_running_services
    start_backend
    start_frontend
    show_status
    
    # Keep script running
    print_status "Services are running. Press Ctrl+C to stop."
    while true; do
        sleep 10
    done
}

# Run main function
main "$@"
