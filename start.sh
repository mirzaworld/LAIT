#!/bin/bash

# LAIT - Enhanced Legal Intelligence System Starter Script
# This script starts both the backend and frontend in separate terminals

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== LAIT - Enhanced Legal Intelligence System ===${NC}"
echo -e "${GREEN}Starting backend and frontend services...${NC}"

# Check if backend server exists
if [ ! -f ./backend/enhanced_app.py ]; then
  echo -e "${YELLOW}Warning: Backend file not found at ./backend/enhanced_app.py${NC}"
  echo "Please make sure your backend is properly set up."
  exit 1
fi

# Start the backend in a new terminal window
osascript -e 'tell application "Terminal"
  do script "cd '"$(pwd)"' && ./run_api.sh"
end tell'

# Wait for backend to initialize
echo "Waiting for backend to initialize..."
sleep 3

# Start the frontend
echo -e "${GREEN}Starting frontend on http://localhost:5174${NC}"
npm run dev
