#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    if ! command_exists node; then
        echo -e "${RED}Node.js is not installed. Please install Node.js v18 or higher.${NC}"
        exit 1
    fi
    
    if ! command_exists python3; then
        echo -e "${RED}Python 3 is not installed. Please install Python 3.10 or higher.${NC}"
        exit 1
    fi
    
    if ! command_exists npm; then
        echo -e "${RED}npm is not installed. Please install npm.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}All prerequisites are satisfied!${NC}"
}

# Function to install dependencies
install_dependencies() {
    echo -e "${BLUE}Installing dependencies...${NC}"
    
    # Frontend dependencies
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
    
    # Backend dependencies
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    
    echo -e "${GREEN}All dependencies installed successfully!${NC}"
}

# Function to start the backend server
start_backend() {
    echo -e "${BLUE}Starting backend server...${NC}"
    cd backend
    source venv/bin/activate
    uvicorn main:app --reload --port 8000 &
    cd ..
    echo -e "${GREEN}Backend server started on http://localhost:8000${NC}"
}

# Function to start the frontend server
start_frontend() {
    echo -e "${BLUE}Starting frontend server...${NC}"
    cd frontend
    npm run dev &
    cd ..
    echo -e "${GREEN}Frontend server started on http://localhost:3000${NC}"
}

# Function to stop all servers
stop_servers() {
    echo -e "${BLUE}Stopping all servers...${NC}"
    pkill -f "uvicorn main:app"
    pkill -f "npm run dev"
    echo -e "${GREEN}All servers stopped${NC}"
}

# Main menu
while true; do
    echo -e "\n${BLUE}QuizForge Launcher${NC}"
    echo "1. Start both frontend and backend"
    echo "2. Start backend only"
    echo "3. Start frontend only"
    echo "4. Install dependencies"
    echo "5. Update dependencies"
    echo "6. Run tests"
    echo "7. Clean up (stop all servers)"
    echo "0. Exit"
    
    read -p "Enter your choice (0-7): " choice
    
    case $choice in
        1)
            check_prerequisites
            start_backend
            start_frontend
            ;;
        2)
            check_prerequisites
            start_backend
            ;;
        3)
            check_prerequisites
            start_frontend
            ;;
        4)
            check_prerequisites
            install_dependencies
            ;;
        5)
            check_prerequisites
            install_dependencies
            ;;
        6)
            echo -e "${YELLOW}Running tests...${NC}"
            # Add test commands here
            ;;
        7)
            stop_servers
            ;;
        0)
            stop_servers
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            ;;
    esac
done 