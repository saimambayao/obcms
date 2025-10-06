# OBCMS Code Quality - Quick Fix Guide

**Generated:** 2025-10-06
**Priority:** CRITICAL → HIGH → MEDIUM → LOW

---

## 🔴 CRITICAL FIXES (Do Now - 30 minutes)

### 1. Fix Syntax Error in common/views.py

**File:** `/src/common/views.py`
**Line:** 1926
**Issue:** Incorrect indentation blocking all analysis tools

**Current Code:**
```python
@login_required
def dashboard_metrics(request):
    """Live metrics HTML (updates every 60s)."""
    from django.http import HttpResponse
from django.db.models import Sum  # ❌ WRONG INDENTATION
    from datetime import timedelta
```

**Fixed Code:**
```python
@login_required
def dashboard_metrics(request):
    """Live metrics HTML (updates every 60s)."""
    from django.http import HttpResponse
    from django.db.models import Sum  # ✅ CORRECT
    from datetime import timedelta
```

**Command:**
```bash
# Edit the file and add 4 spaces before "from django.db.models import Sum"
```

**Impact:** Unblocks code analysis tools, prevents potential runtime errors
**Time:** 2 minutes

---

### 2. Replace MD5 with SHA-256 (Security)

#### Fix #1: Cache Service

**File:** `/src/ai_assistant/services/cache_service.py`
**Line:** 206

**Before:**
```python
param_hash = hashlib.md5(param_string.encode()).hexdigest()
```

**After:**
```python
param_hash = hashlib.sha256(param_string.encode()).hexdigest()
```

#### Fix #2: Embedding Service

**File:** `/src/ai_assistant/services/embedding_service.py`
**Line:** 184

**Before:**
```python
return hashlib.md5(text.encode('utf-8')).hexdigest()
```

**After:**
```python
return hashlib.sha256(text.encode('utf-8')).hexdigest()
```

**Impact:** Resolves 2 high-severity security warnings
**Time:** 5 minutes

---

### 3. Remove Unused Imports (Automated)

**Issue:** 523 unused imports across codebase

**Command:**
```bash
cd /path/to/obcms/src
source ../venv/bin/activate

# Install autoflake
pip install autoflake

# Dry run first (see what will be removed)
autoflake --remove-all-unused-imports --recursive .

# Apply changes
autoflake --remove-all-unused-imports --in-place --recursive .

# Exclude migrations and cache
autoflake --remove-all-unused-imports --in-place --recursive \
  --exclude=migrations,__pycache__,venv,static,media .
```

**Impact:** Reduces flake8 issues from 2,149 → ~1,600
**Time:** 15 minutes (mostly automated)

---

## 🟡 HIGH PRIORITY (This Week)

### 4. Fix Bare Except Clauses

**Issue:** 5 instances of bare `except:` (catches all exceptions, including KeyboardInterrupt)

**Pattern to Find:**
```bash
cd src
grep -rn "except:" --include="*.py" . | grep -v "except Exception" | grep -v "#"
```

**Fix:**
```python
# ❌ Bad
try:
    something()
except:
    pass

# ✅ Good
try:
    something()
except Exception as e:
    logger.error(f"Error: {e}")
```

**Impact:** Better error handling and debugging
**Time:** 30 minutes

---

### 5. Fix Undefined Name Errors (F821)

**Issue:** 20 instances of undefined `OBCCommunity`

**Find:**
```bash
cd src
flake8 . | grep F821
```

**Likely Causes:**
- Missing imports
- Typos in model names
- Circular import issues

**Fix Pattern:**
```python
# Add missing import
from communities.models import OBCCommunity
```

**Time:** 1 hour

---

### 6. Configure Black Formatter

**Purpose:** Auto-fix 1,119 line length violations

**Setup:**
```bash
cd /path/to/obcms
source venv/bin/activate
pip install black

# Create pyproject.toml
cat > pyproject.toml <<EOF
[tool.black]
line-length = 120
target-version = ['py312']
exclude = '''
/(
    \.git
  | \.venv
  | venv
  | migrations
  | __pycache__
  | static
  | media
)/
'''
EOF

# Format entire codebase
black src/

# Format specific file
black src/common/forms/work_items.py
```

**Impact:** Fixes 1,119 E501 line-too-long errors automatically
**Time:** 20 minutes setup + 10 minutes to run

---

## 📋 MEDIUM PRIORITY (Next 2 Weeks)

### 7. Refactor Large Files

**Target Files:**

| File | Lines | Action |
|------|-------|--------|
| `common/views/management.py` | 5,373 | Split into 5-6 modules |
| `mana/models.py` | 3,662 | Separate by domain (Assessment, Need, etc.) |
| `common/views/mana.py` | 3,314 | Extract service layer |
| `communities/models.py` | 2,578 | Split into geographic/demographic modules |

**Strategy Example: mana/models.py**

```bash
# Create new structure
mkdir -p mana/models
touch mana/models/__init__.py
touch mana/models/assessment.py
touch mana/models/need.py
touch mana/models/activity.py

# Move related models to respective files
# Update __init__.py with imports
```

**Time per file:** 4-6 hours
**Total time:** 2-3 days

---

### 8. Refactor High-Complexity Functions

**Top 3 Priority Functions:**

#### 1. import_moa_ppas.py:Command.handle (Complexity: 56)

**File:** `/src/data_imports/management/commands/import_moa_ppas.py`
**Line:** 40
**Current Grade:** F

**Strategy:**
- Extract validation logic into separate methods
- Create helper functions for PPA creation
- Use early returns to reduce nesting

**Target:** Reduce complexity to < 15 (Grade B)

#### 2. RecurringEventPattern.get_occurrences (Complexity: 48)

**File:** `/src/common/models.py`
**Line:** 888
**Current Grade:** F

**Strategy:**
- Extract date calculation logic
- Separate occurrence filtering
- Use generator for large date ranges

**Target:** Reduce complexity to < 15 (Grade B)

#### 3. event_edit_instance (Complexity: 25)

**File:** `/src/coordination/views.py`
**Line:** 568
**Current Grade:** D

**Strategy:**
- Extract form processing logic
- Create service layer for event updates
- Use form mixins

**Target:** Reduce complexity to < 12 (Grade C)

**Total Time:** 2-3 days

---

### 9. Configure Pre-commit Hooks

**Setup:**

```bash
cd /path/to/obcms
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml <<'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        args: [--line-length=120]
        exclude: migrations/

  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=120, --extend-ignore=E203,W503]
        exclude: migrations/

  - repo: https://github.com/PyCQA/autoflake
    rev: v2.2.1
    hooks:
      - id: autoflake
        args: [--remove-all-unused-imports, --in-place]
        exclude: migrations/

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black, --line-length=120]
        exclude: migrations/

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
        exclude: migrations/
      - id: end-of-file-fixer
        exclude: migrations/
      - id: check-yaml
      - id: check-added-large-files
        args: [--maxkb=1000]
EOF

# Install hooks
pre-commit install

# Test on all files (optional)
pre-commit run --all-files
```

**Impact:** Prevents future code quality issues
**Time:** 30 minutes

---

## 🔵 LOW PRIORITY (Backlog)

### 10. Improve Class Documentation

**Current:** 69.3%
**Target:** 85%+

**Focus Areas:**
1. Model classes in `mana/models.py`
2. Service classes in `ai_services/`
3. Form classes in `common/forms/`

**Template:**
```python
class CommunityDataValidator:
    """
    Validates and suggests improvements for OBC community data.

    This service uses AI to identify missing or inconsistent data
    in community profiles and provides actionable suggestions.

    Attributes:
        confidence_threshold (float): Minimum confidence for suggestions (default: 0.7)

    Example:
        >>> validator = CommunityDataValidator()
        >>> suggestions = validator.suggest_missing_data(community_id=123)
    """
```

**Time:** 4-6 hours

---

### 11. Address TODOs Systematically

**Total TODOs:** 33

**Priority Breakdown:**

#### High Priority (8 TODOs): WorkItem Migration
```bash
# Find all StaffTask → WorkItem migration TODOs
grep -rn "TODO.*StaffTask\|TODO.*WorkItem" src/
```

**Files:**
- `common/views/management.py:77`
- `common/services/calendar.py:198, 915`
- `common/views.py:568-591`

**Time:** 1 week

#### Medium Priority (10 TODOs): API Migration
```bash
# Find API versioning TODOs
grep -rn "TODO.*api/v1\|TODO.*Implement these views" src/
```

**Time:** 2 weeks

---

## 📊 Progress Tracking

### Completion Checklist

#### Week 1 (CRITICAL + Some HIGH)
- [ ] Fix syntax error in `common/views.py`
- [ ] Replace MD5 with SHA-256 (2 files)
- [ ] Remove unused imports (automated)
- [ ] Configure Black formatter
- [ ] Run Black on entire codebase
- [ ] Fix bare except clauses (5 instances)

**Expected Impact:**
- Flake8 issues: 2,149 → ~400
- Security issues (High): 2 → 0
- Code quality score: B+ (82) → A- (87)

#### Week 2-3 (HIGH Priority)
- [ ] Fix undefined name errors (F821)
- [ ] Configure pre-commit hooks
- [ ] Refactor `import_moa_ppas.py:Command.handle`
- [ ] Refactor `RecurringEventPattern.get_occurrences`
- [ ] Begin splitting `common/views/management.py`

**Expected Impact:**
- Complexity issues: Reduced by 40%
- Code quality score: A- (87) → A (90)

#### Month 2 (MEDIUM Priority)
- [ ] Complete file splitting (4 large files)
- [ ] Refactor remaining high-complexity functions
- [ ] Improve class documentation to 85%
- [ ] Address WorkItem migration TODOs

**Expected Impact:**
- Maintainability: All files > B grade
- Code quality score: A (90) → A+ (95)

---

## 🛠️ Quick Commands Reference

```bash
# Activate environment
cd /path/to/obcms
source venv/bin/activate

# Run quality checks
flake8 src/ --max-line-length=120 --statistics
radon cc src/ -a -s --min C
bandit -r src/ -ll -i

# Auto-format
black src/ --line-length=120
autoflake --remove-all-unused-imports --in-place --recursive src/

# Find specific issues
grep -rn "except:" src/ --include="*.py"  # Bare excepts
grep -rn "TODO\|FIXME" src/ --include="*.py"  # Technical debt
flake8 src/ | grep F401  # Unused imports
flake8 src/ | grep F821  # Undefined names

# Install quality tools
pip install black autoflake flake8 radon bandit isort pre-commit
```

---

## 📈 Expected Outcomes

### Before Fixes
- **Flake8 Issues:** 2,149
- **Security (High):** 2
- **Code Quality:** B+ (82/100)

### After Week 1
- **Flake8 Issues:** ~400 (81% reduction)
- **Security (High):** 0 (100% fixed)
- **Code Quality:** A- (87/100)

### After Month 2
- **Flake8 Issues:** < 100
- **Maintainability:** All files B+ or higher
- **Code Quality:** A+ (95/100)

---

**For detailed analysis, see:** `docs/testing/CODE_QUALITY_ANALYSIS_REPORT.md`

**Report Generated:** 2025-10-06
**Next Review:** 2025-11-06
