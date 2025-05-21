#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${BLUE}[QuizForge]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[Success]${NC} $1"
}

print_error() {
    echo -e "${RED}[Error]${NC} $1"
}

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    print_message "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Python 3.12 if not installed
if ! command -v python3.12 &> /dev/null; then
    print_message "Installing Python 3.12..."
    brew install python@3.12
fi

# Install Node.js if not installed
if ! command -v node &> /dev/null; then
    print_message "Installing Node.js..."
    brew install node
fi

# Setup Backend
print_message "Setting up backend..."
cd backend

# Create and activate virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    print_message "Created .env file. Please update it with your configuration."
fi

# Setup Frontend
print_message "Setting up frontend..."
cd ../frontend

# Install Node.js dependencies
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env
fi

print_success "Setup completed successfully!"
print_message "To start the application:"
print_message "1. Start the backend: cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000"
print_message "2. Start the frontend: cd frontend && npm run dev" 