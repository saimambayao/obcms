#!/bin/bash
#
# Quick AI Services Testing Script (Unit Tests Only)
# Runs fast unit tests without Django database initialization
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$BASE_DIR/src"

echo -e "${BLUE}Quick AI Services Testing${NC}"
echo -e "${BLUE}=========================${NC}"
echo ""

# Activate virtual environment
source "$BASE_DIR/venv/bin/activate"
cd "$SRC_DIR"

# Run unit tests only (no database required)
echo -e "${YELLOW}1. Gemini Service Unit Tests${NC}"
python -m pytest ai_assistant/tests/test_gemini_service.py::TestGeminiService -v -k "not integration" --tb=short

echo ""
echo -e "${YELLOW}2. Token and Cost Calculation Tests${NC}"
python -m pytest ai_assistant/tests/test_gemini_service.py::TestGeminiService::test_token_estimation -v
python -m pytest ai_assistant/tests/test_gemini_service.py::TestGeminiService::test_cost_calculation -v

echo ""
echo -e "${YELLOW}3. Cache Service Tests${NC}"
python -m pytest ai_assistant/tests/test_cache_service.py -v --tb=short 2>&1 | head -50

echo ""
echo -e "${GREEN}Quick tests complete!${NC}"
echo ""
echo "To run full integration tests (slower), use:"
echo "  ./scripts/test_ai_comprehensive.sh"
