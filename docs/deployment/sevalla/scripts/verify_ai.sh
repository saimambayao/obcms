#!/bin/bash
# OBCMS AI Verification Script
# Quick verification that AI features are working

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_ROOT/src"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  OBCMS AI Verification${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Activate venv
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
else
    echo -e "${RED}Virtual environment not found${NC}"
    exit 1
fi

cd "$SRC_DIR"

# Test 1: AI Service Imports
echo -e "${BLUE}Test 1: AI Service Imports${NC}"
python3 << 'EOF'
try:
    from ai_assistant.services import GeminiService, EmbeddingService, VectorStore
    from ai_assistant.services import CacheService, SimilaritySearchService
    from ai_assistant.utils import CostTracker, ErrorHandler
    print("✓ All core services import successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)
EOF
echo ""

# Test 2: Module AI Services
echo -e "${BLUE}Test 2: Module AI Services${NC}"
python3 << 'EOF'
try:
    from communities.ai_services import CommunityDataValidator, CommunityNeedsClassifier
    print("✓ Communities AI services OK")
except ImportError as e:
    print(f"⚠ Communities AI: {e}")

try:
    from mana.ai_services import ResponseAnalyzer, ThemeExtractor, NeedsExtractor
    print("✓ MANA AI services OK")
except ImportError as e:
    print(f"⚠ MANA AI: {e}")

try:
    from coordination.ai_services import StakeholderMatcher
    print("✓ Coordination AI services OK")
except ImportError as e:
    print(f"⚠ Coordination AI: {e}")

try:
    from common.ai_services.chat import get_conversational_assistant
    print("✓ Chat AI services OK")
except ImportError as e:
    print(f"⚠ Chat AI: {e}")
EOF
echo ""

# Test 3: Database Models
echo -e "${BLUE}Test 3: Database Models${NC}"
python3 manage.py shell << 'EOF'
from ai_assistant.models import AIOperation, DocumentEmbedding
from common.models import ChatMessage
print("✓ AI models accessible")
EOF
echo ""

# Test 4: Management Commands
echo -e "${BLUE}Test 4: Management Commands${NC}"
if python3 manage.py help ai_health_check > /dev/null 2>&1; then
    echo "✓ ai_health_check command available"
else
    echo "⚠ ai_health_check command not found"
fi

if python3 manage.py help index_communities > /dev/null 2>&1; then
    echo "✓ index_communities command available"
else
    echo "⚠ index_communities command not found"
fi
echo ""

# Test 5: Configuration
echo -e "${BLUE}Test 5: Configuration Check${NC}"
python3 manage.py shell << 'EOF'
import os
from django.conf import settings

# Check GOOGLE_API_KEY
if hasattr(settings, 'GOOGLE_API_KEY') and settings.GOOGLE_API_KEY:
    print("✓ GOOGLE_API_KEY configured")
else:
    print("⚠ GOOGLE_API_KEY not set (AI features limited)")

# Check Redis
if hasattr(settings, 'REDIS_URL'):
    print(f"✓ REDIS_URL: {settings.REDIS_URL}")
else:
    print("⚠ REDIS_URL not configured")

# Check ai_assistant in INSTALLED_APPS
if 'ai_assistant' in settings.INSTALLED_APPS:
    print("✓ ai_assistant app installed")
else:
    print("✗ ai_assistant NOT in INSTALLED_APPS")
EOF
echo ""

# Test 6: Vector Indices Directory
echo -e "${BLUE}Test 6: Vector Storage${NC}"
VECTOR_DIR="$SRC_DIR/ai_assistant/vector_indices"
if [ -d "$VECTOR_DIR" ]; then
    echo "✓ Vector indices directory exists"
    FILE_COUNT=$(ls -1 "$VECTOR_DIR" 2>/dev/null | wc -l)
    echo "  Files: $FILE_COUNT"
else
    echo "⚠ Vector indices directory not found"
fi
echo ""

# Test 7: Dependencies
echo -e "${BLUE}Test 7: Key Dependencies${NC}"
python3 << 'EOF'
import sys

deps = {
    'google.generativeai': 'Google Gemini',
    'faiss': 'FAISS (vector store)',
    'sentence_transformers': 'Sentence Transformers',
    'redis': 'Redis',
    'celery': 'Celery',
}

for module, name in deps.items():
    try:
        __import__(module)
        print(f"✓ {name}")
    except ImportError:
        print(f"✗ {name} NOT installed")
EOF
echo ""

# Test 8: Run AI Health Check
echo -e "${BLUE}Test 8: AI Health Check${NC}"
python3 manage.py ai_health_check
echo ""

# Summary
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}  Verification Complete${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo "If all tests passed, AI features are ready to use!"
echo ""
echo "Next: Start the development server"
echo "  cd src && python3 manage.py runserver"
