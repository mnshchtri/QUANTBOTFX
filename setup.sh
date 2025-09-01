#!/bin/bash

# QuantBotForex Setup Script
# This script sets up the development environment for QuantBotForex

set -e  # Exit on any error

echo "🚀 QuantBotForex Setup Script"
echo "================================"

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

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_status "Python $PYTHON_VERSION found"
        
        # Check Python version compatibility
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
            print_warning "Python 3.9+ recommended. Current version: $PYTHON_VERSION"
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi
}

# Check if Node.js is installed
check_nodejs() {
    print_status "Checking Node.js installation..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        print_status "Node.js $NODE_VERSION found"
        
        # Check Node.js version compatibility
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
        if [ "$NODE_MAJOR" -lt 16 ]; then
            print_warning "Node.js 16+ recommended. Current version: $NODE_VERSION"
        fi
    else
        print_error "Node.js is not installed. Please install Node.js 16+ first."
        exit 1
    fi
}

# Create virtual environment
setup_python_env() {
    print_header "Setting up Python environment..."
    
    if [ ! -d ".venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv .venv
    else
        print_status "Virtual environment already exists"
    fi
    
    print_status "Activating virtual environment..."
    source .venv/bin/activate
    
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    print_status "Installing Python dependencies..."
    
    # Install backend dependencies first
    if [ -f "backend/requirements.txt" ]; then
        print_status "Installing backend dependencies..."
        pip install -r backend/requirements.txt
    fi
    
    # Install root requirements if they exist
    if [ -f "requirements.txt" ]; then
        print_status "Installing additional dependencies..."
        pip install -r requirements.txt
    fi
    
    print_status "Python dependencies installed successfully"
}

# Setup frontend
setup_frontend() {
    print_header "Setting up frontend..."
    
    if [ ! -d "frontend" ]; then
        print_error "Frontend directory not found. Please ensure you're in the project root."
        exit 1
    fi
    
    cd frontend
    
    print_status "Installing Node.js dependencies..."
    npm install
    
    cd ..
}

# Create environment file
setup_env() {
    print_header "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            print_status "Creating .env file from template..."
            cp env.example .env
            print_warning "Please edit .env file with your OANDA API credentials"
        else
            print_warning "No env.example found. Please create .env manually."
        fi
    else
        print_status ".env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_header "Creating project directories..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p models
    mkdir -p storage
    mkdir -p tests
    mkdir -p docs
    mkdir -p backend/logs
    mkdir -p frontend/logs
    
    print_status "Directories created successfully"
}

# Check OANDA API setup
check_oanda_setup() {
    print_header "Checking OANDA API setup..."
    
    # Check config.yaml first
    if [ -f "config.yaml" ]; then
        if grep -q "practice-API-KEY-HERE" config.yaml; then
            print_warning "OANDA API key in config.yaml appears to be placeholder"
            print_status "Please update config.yaml with your real OANDA API key"
        else
            print_status "OANDA API key in config.yaml appears to be configured"
        fi
    fi
    
    # Check .env file
    if [ -f ".env" ]; then
        if grep -q "your_oanda_api_key_here" .env; then
            print_warning "OANDA API key in .env not configured. Please update .env file with your credentials."
        else
            print_status "OANDA API key in .env appears to be configured"
        fi
    fi
    
    print_status "Get your API key from: https://www.oanda.com/account/login"
}

# Check system health
check_system_health() {
    print_header "Checking system health..."
    
    # Check if backend can start
    if [ -f "backend/app.py" ]; then
        print_status "Backend app.py found"
    else
        print_error "Backend app.py not found"
    fi
    
    # Check if frontend package.json exists
    if [ -f "frontend/package.json" ]; then
        print_status "Frontend package.json found"
    else
        print_error "Frontend package.json not found"
    fi
    
    # Check config files
    if [ -f "config.yaml" ]; then
        print_status "config.yaml found"
    else
        print_warning "config.yaml not found"
    fi
}

# Display next steps
show_next_steps() {
    print_header "Setup Complete! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Ensure your OANDA API key is configured in config.yaml or .env"
    echo "2. Start the backend: cd backend && python app.py"
    echo "3. Start the frontend: cd frontend && npm start"
    echo "4. Access the application: http://localhost:3000"
    echo "5. Backend API docs: http://localhost:8000/docs"
    echo ""
    echo "Current configuration:"
    echo "- Backend: FastAPI on port 8000"
    echo "- Frontend: React on port 3000"
    echo "- Data Source: OANDA API (practice environment)"
    echo "- No fake data: System uses 100% real market data"
    echo ""
    echo "For more information, see README.md"
}

# Main setup function
main() {
    print_header "Starting QuantBotForex setup..."
    
    check_python
    check_nodejs
    setup_python_env
    setup_frontend
    setup_env
    create_directories
    check_oanda_setup
    check_system_health
    show_next_steps
}

# Run main function
main "$@" 