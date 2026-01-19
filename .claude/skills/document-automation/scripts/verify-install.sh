#!/bin/bash
# Verify Document Automation installation
# Usage: ./verify-install.sh

set -e

echo "=========================================="
echo "Document Automation - Installation Checker"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

info() {
    echo -e "       $1"
}

# Track overall status
STATUS=0

# Check Python
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    pass "Python 3 installed: $PYTHON_VERSION"

    # Check minimum version (3.8+)
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
        pass "Python version meets requirements (3.8+)"
    else
        fail "Python 3.8+ required, found $PYTHON_VERSION"
        STATUS=1
    fi
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    warn "Using 'python' command: $PYTHON_VERSION"
else
    fail "Python not found"
    STATUS=1
fi
echo ""

# Check pip
echo "Checking pip installation..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version 2>&1 | cut -d' ' -f2)
    pass "pip installed: $PIP_VERSION"
elif command -v pip &> /dev/null; then
    PIP_VERSION=$(pip --version 2>&1 | cut -d' ' -f2)
    pass "pip installed: $PIP_VERSION"
else
    fail "pip not found"
    STATUS=1
fi
echo ""

# Check Git
echo "Checking Git installation..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version 2>&1 | cut -d' ' -f3)
    pass "Git installed: $GIT_VERSION"
else
    fail "Git not found"
    STATUS=1
fi
echo ""

# Check GitHub CLI (optional)
echo "Checking GitHub CLI (optional)..."
if command -v gh &> /dev/null; then
    GH_VERSION=$(gh --version 2>&1 | head -n1 | cut -d' ' -f3)
    pass "GitHub CLI installed: $GH_VERSION"

    # Check if authenticated
    if gh auth status &> /dev/null; then
        pass "GitHub CLI authenticated"
    else
        warn "GitHub CLI not authenticated"
        info "Run 'gh auth login' to authenticate"
    fi
else
    warn "GitHub CLI not installed (optional, but recommended)"
    info "Install with: brew install gh (macOS) or winget install GitHub.cli (Windows)"
fi
echo ""

# Check required Python packages
echo "Checking required Python packages..."
REQUIRED_PACKAGES=("mcp" "fastapi" "pydantic" "httpx" "aiofiles" "jinja2" "markdown")

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $pkg" 2>/dev/null; then
        VERSION=$(python3 -c "import $pkg; print(getattr($pkg, '__version__', 'installed'))" 2>/dev/null || echo "installed")
        pass "$pkg: $VERSION"
    else
        fail "$pkg not installed"
        STATUS=1
    fi
done
echo ""

# Check Document Automation project
echo "Checking Document Automation project..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")")"

if [ -f "$PROJECT_ROOT/src/main.py" ]; then
    pass "Project found at: $PROJECT_ROOT"
else
    fail "Project not found. Expected at: $PROJECT_ROOT"
    info "Make sure you're running from the Document-Automation directory"
    STATUS=1
fi

if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    pass "requirements.txt found"
else
    warn "requirements.txt not found"
fi

if [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
    pass "pyproject.toml found"
else
    warn "pyproject.toml not found"
fi
echo ""

# Check environment variables
echo "Checking environment variables..."
if [ -n "$GITHUB_TOKEN" ]; then
    TOKEN_PREFIX="${GITHUB_TOKEN:0:10}..."
    pass "GITHUB_TOKEN set: $TOKEN_PREFIX"
else
    warn "GITHUB_TOKEN not set"
    info "Private repository access will not work"
    info "Set with: export GITHUB_TOKEN=ghp_your_token"
fi
echo ""

# Test import
echo "Testing module imports..."
if python3 -c "from src.analyzers.codebase_analyzer import CodebaseAnalyzer; print('OK')" 2>/dev/null; then
    pass "Core modules importable"
else
    fail "Cannot import core modules"
    info "Try: cd $PROJECT_ROOT && pip install -e ."
    STATUS=1
fi
echo ""

# Summary
echo "=========================================="
if [ $STATUS -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    echo "Document Automation is ready to use."
else
    echo -e "${RED}Some checks failed.${NC}"
    echo "Please fix the issues above before using."
fi
echo "=========================================="

exit $STATUS
