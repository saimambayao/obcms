#!/bin/bash
# OBCMS AI Deployment Script
# Automates the deployment of all AI features

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_ROOT/src"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  OBCMS AI Deployment Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/requirements/base.txt" ]; then
    echo -e "${RED}Error: Cannot find requirements/base.txt${NC}"
    echo -e "${RED}Please run this script from the OBCMS root directory${NC}"
    exit 1
fi

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Step 1: Check Python version
echo -e "${BLUE}Step 1: Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_status "Python $PYTHON_VERSION found"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    print_status "Python $PYTHON_VERSION found"
    PYTHON_CMD="python"
else
    print_error "Python not found. Please install Python 3.12+"
    exit 1
fi

# Check Python version is 3.12+
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ]); then
    print_error "Python 3.12+ required. Current: $PYTHON_VERSION"
    exit 1
fi

echo ""

# Step 2: Check virtual environment
echo -e "${BLUE}Step 2: Checking virtual environment...${NC}"
if [ -d "$PROJECT_ROOT/venv" ]; then
    print_status "Virtual environment found at $PROJECT_ROOT/venv"

    # Activate virtual environment
    if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
        source "$PROJECT_ROOT/venv/bin/activate"
        print_status "Virtual environment activated"
    else
        print_error "Cannot find venv/bin/activate"
        exit 1
    fi
else
    print_warning "Virtual environment not found"
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv "$PROJECT_ROOT/venv"
    source "$PROJECT_ROOT/venv/bin/activate"
    print_status "Virtual environment created and activated"
fi

echo ""

# Step 3: Install/Update dependencies
echo -e "${BLUE}Step 3: Installing AI dependencies...${NC}"
print_info "This may take several minutes..."

pip install --upgrade pip > /dev/null 2>&1
print_status "pip upgraded"

pip install -r "$PROJECT_ROOT/requirements/base.txt" --quiet
print_status "All dependencies installed"

echo ""

# Step 4: Check environment variables
echo -e "${BLUE}Step 4: Checking environment variables...${NC}"

if [ ! -f "$PROJECT_ROOT/.env" ]; then
    print_warning ".env file not found"
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        print_status ".env created"
        print_warning "Please configure GOOGLE_API_KEY in .env"
    else
        print_error ".env.example not found"
    fi
else
    print_status ".env file exists"
fi

# Check for GOOGLE_API_KEY
if grep -q "^GOOGLE_API_KEY=.*[^=]$" "$PROJECT_ROOT/.env" 2>/dev/null; then
    print_status "GOOGLE_API_KEY is configured"
else
    print_warning "GOOGLE_API_KEY not set in .env"
    echo -e "${YELLOW}AI features will work with reduced functionality${NC}"
fi

echo ""

# Step 5: Run migrations
echo -e "${BLUE}Step 5: Running database migrations...${NC}"
cd "$SRC_DIR"

$PYTHON_CMD manage.py migrate --noinput
print_status "All migrations applied"

echo ""

# Step 6: Create vector indices directory
echo -e "${BLUE}Step 6: Setting up vector indices...${NC}"
VECTOR_DIR="$SRC_DIR/ai_assistant/vector_indices"
if [ ! -d "$VECTOR_DIR" ]; then
    mkdir -p "$VECTOR_DIR"
    print_status "Vector indices directory created"
else
    print_status "Vector indices directory exists"
fi

echo ""

# Step 7: Test AI services
echo -e "${BLUE}Step 7: Testing AI services...${NC}"

# Test imports
$PYTHON_CMD -c "
from ai_assistant.services import GeminiService
from ai_assistant.services import EmbeddingService
from ai_assistant.services import VectorStore
print('✓ All AI services import successfully')
" 2>&1

if [ $? -eq 0 ]; then
    print_status "AI service imports successful"
else
    print_error "AI service imports failed"
    exit 1
fi

# Run health check
if $PYTHON_CMD manage.py ai_health_check 2>&1 | grep -q "HEALTH CHECK"; then
    print_status "AI health check passed"
else
    print_warning "AI health check reported issues (check output above)"
fi

echo ""

# Step 8: Check for initial data
echo -e "${BLUE}Step 8: Checking for data to index...${NC}"

# Check if we have communities to index
COMMUNITY_COUNT=$($PYTHON_CMD manage.py shell -c "
from communities.models import BarangayOBC
print(BarangayOBC.objects.count())
" 2>/dev/null || echo "0")

if [ "$COMMUNITY_COUNT" -gt 0 ]; then
    print_status "Found $COMMUNITY_COUNT communities"

    read -p "$(echo -e ${YELLOW}Do you want to index communities now? [y/N]: ${NC})" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Indexing communities...${NC}"
        $PYTHON_CMD manage.py index_communities
        print_status "Communities indexed"
    fi
else
    print_info "No communities found to index"
fi

echo ""

# Step 9: Create superuser if needed
echo -e "${BLUE}Step 9: Checking for superuser...${NC}"
SUPERUSER_EXISTS=$($PYTHON_CMD manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
print('yes' if User.objects.filter(is_superuser=True).exists() else 'no')
" 2>/dev/null || echo "no")

if [ "$SUPERUSER_EXISTS" = "yes" ]; then
    print_status "Superuser exists"
else
    print_warning "No superuser found"
    read -p "$(echo -e ${YELLOW}Create superuser now? [y/N]: ${NC})" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $PYTHON_CMD manage.py createsuperuser
    fi
fi

echo ""

# Step 10: Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}✓${NC} AI infrastructure deployed"
echo -e "${GREEN}✓${NC} Database migrations applied"
echo -e "${GREEN}✓${NC} Dependencies installed"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo -e "1. ${YELLOW}Configure API Key:${NC}"
echo -e "   Edit .env and add: GOOGLE_API_KEY=your_key_here"
echo ""
echo -e "2. ${YELLOW}Start Development Server:${NC}"
echo -e "   cd src && python manage.py runserver"
echo ""
echo -e "3. ${YELLOW}Start Celery Worker (in new terminal):${NC}"
echo -e "   cd src && celery -A obc_management worker -l info"
echo ""
echo -e "4. ${YELLOW}Start Celery Beat (in new terminal):${NC}"
echo -e "   cd src && celery -A obc_management beat -l info"
echo ""
echo -e "5. ${YELLOW}Access Admin:${NC}"
echo -e "   http://localhost:8000/admin/"
echo ""
echo -e "6. ${YELLOW}Test AI Features:${NC}"
echo -e "   - Communities AI: http://localhost:8000/communities/"
echo -e "   - MANA AI: http://localhost:8000/mana/"
echo -e "   - Chat Assistant: Look for chat icon bottom-right"
echo ""
echo -e "${GREEN}Documentation:${NC}"
echo -e "   - Quick Start: docs/ai/AI_QUICK_START.md"
echo -e "   - Full Guide: docs/ai/AI_STRATEGY_COMPREHENSIVE.md"
echo -e "   - Checklist: docs/ai/AI_IMPLEMENTATION_CHECKLIST.md"
echo ""
echo -e "${BLUE}========================================${NC}"
