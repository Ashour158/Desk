#!/bin/bash
# Setup script for Django Multi-Tenant Helpdesk & FSM Platform
# This script sets up the development environment in one command

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}Django Helpdesk Platform Setup${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Step 2: Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "${YELLOW}Step 3: Upgrading pip...${NC}"
if ! pip install --upgrade pip > /tmp/pip_upgrade.log 2>&1; then
    echo -e "${RED}Error: pip upgrade failed. See details below:${NC}"
    cat /tmp/pip_upgrade.log
    exit 1
fi
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install Python dependencies
echo -e "${YELLOW}Step 4: Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
elif [ -f "requirements/base.txt" ]; then
    pip install -r requirements/base.txt > /dev/null 2>&1
    echo -e "${YELLOW}✓ Python dependencies installed from requirements/base.txt${NC}"
else
    echo -e "${RED}Warning: Neither requirements.txt nor requirements/base.txt found${NC}"
fi

# Install pre-commit hooks
echo -e "${YELLOW}Step 5: Installing pre-commit hooks...${NC}"
if command -v pre-commit &> /dev/null; then
    pre-commit install > /dev/null 2>&1
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
else
    pip install pre-commit > /dev/null 2>&1
    pre-commit install > /dev/null 2>&1
    echo -e "${GREEN}✓ Pre-commit installed and hooks configured${NC}"
fi

# Setup environment file
echo -e "${YELLOW}Step 6: Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo -e "${GREEN}✓ Environment file created from env.example${NC}"
        echo -e "${YELLOW}  Please edit .env with your configuration${NC}"
    else
        echo -e "${RED}Warning: env.example not found${NC}"
    fi
else
    echo -e "${GREEN}✓ Environment file already exists${NC}"
fi

# Check if Node.js is installed (for frontend)
echo -e "${YELLOW}Step 7: Checking Node.js installation...${NC}"
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Node.js is installed (version: $(node -v))${NC}"
    
    # Install frontend dependencies
    FRONTEND_DIRS=("customer-portal" "realtime-service")
    for dir in "${FRONTEND_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            echo -e "${YELLOW}Step 8: Installing dependencies in $dir...${NC}"
            cd "$dir"
            npm ci > /dev/null 2>&1
            cd ..
            echo -e "${GREEN}✓ Dependencies installed in $dir${NC}"
        fi
    done
else
    echo -e "${YELLOW}⚠ Node.js not installed (required for frontend)${NC}"
fi

# Database migrations
echo -e "${YELLOW}Step 9: Running database migrations...${NC}"
cd core
python manage.py migrate > /dev/null 2>&1
echo -e "${GREEN}✓ Database migrations completed${NC}"

# Collect static files
echo -e "${YELLOW}Step 10: Collecting static files...${NC}"
python manage.py collectstatic --noinput > /dev/null 2>&1
echo -e "${GREEN}✓ Static files collected${NC}"

cd ..

echo ""
echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}✓ Setup completed successfully!${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Edit .env file with your configuration"
echo -e "  2. Create a superuser: ${GREEN}cd core && python manage.py createsuperuser${NC}"
echo -e "  3. Run the development server: ${GREEN}cd core && python manage.py runserver${NC}"
echo -e "  4. Run tests: ${GREEN}python -m pytest tests/${NC}"
echo ""
echo -e "${YELLOW}For more information, see README.md${NC}"
