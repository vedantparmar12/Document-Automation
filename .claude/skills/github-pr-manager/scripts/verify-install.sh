#!/bin/bash
# verify-install.sh - Verify GitHub PR Manager skill installation
# Usage: ./verify-install.sh

set -e

echo "========================================"
echo "GitHub PR Manager Skill - Installation Verification"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track issues
ISSUES=0

# Function to check file exists
check_file() {
  if [ -f "$1" ]; then
    echo -e "${GREEN}✓${NC} $1"
    return 0
  else
    echo -e "${RED}✗${NC} $1 (missing)"
    ISSUES=$((ISSUES + 1))
    return 1
  fi
}

# Function to check directory exists
check_dir() {
  if [ -d "$1" ]; then
    echo -e "${GREEN}✓${NC} $1"
    return 0
  else
    echo -e "${RED}✗${NC} $1 (missing)"
    ISSUES=$((ISSUES + 1))
    return 1
  fi
}

# Function to check command exists
check_command() {
  if command -v $1 &> /dev/null; then
    VERSION=$($1 --version 2>&1 | head -n1)
    echo -e "${GREEN}✓${NC} $1 installed: $VERSION"
    return 0
  else
    echo -e "${YELLOW}⚠${NC} $1 not installed (required for skill to work)"
    ISSUES=$((ISSUES + 1))
    return 1
  fi
}

echo "1. Checking Skill Structure"
echo "-----------------------------------"

SKILL_DIR=".claude/skills/github-pr-manager"

check_dir "$SKILL_DIR"
check_file "$SKILL_DIR/SKILL.md"
check_file "$SKILL_DIR/README.md"
check_file "$SKILL_DIR/PR-OPERATIONS.md"
check_file "$SKILL_DIR/EXAMPLES.md"
check_file "$SKILL_DIR/QUICKSTART.md"
check_dir "$SKILL_DIR/scripts"
check_file "$SKILL_DIR/scripts/analyze-pr.py"
check_file "$SKILL_DIR/scripts/chunk-diff.sh"
check_file "$SKILL_DIR/scripts/review-helper.sh"
check_file "$SKILL_DIR/scripts/comment-manager.sh"

echo ""
echo "2. Checking Required Tools"
echo "-----------------------------------"

check_command "gh"
check_command "git"
check_command "python3" || check_command "python"
check_command "jq"

echo ""
echo "3. Checking GitHub Authentication"
echo "-----------------------------------"

if command -v gh &> /dev/null; then
  if gh auth status &> /dev/null; then
    USERNAME=$(gh api user --jq '.login' 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✓${NC} Authenticated as: $USERNAME"
  else
    echo -e "${YELLOW}⚠${NC} Not authenticated with GitHub"
    echo "  Run: gh auth login"
    ISSUES=$((ISSUES + 1))
  fi
else
  echo -e "${YELLOW}⚠${NC} Cannot check authentication (gh not installed)"
fi

echo ""
echo "4. Checking Script Permissions"
echo "-----------------------------------"

if [ -x "$SKILL_DIR/scripts/analyze-pr.py" ]; then
  echo -e "${GREEN}✓${NC} analyze-pr.py is executable"
else
  echo -e "${YELLOW}⚠${NC} analyze-pr.py is not executable"
  echo "  Run: chmod +x $SKILL_DIR/scripts/analyze-pr.py"
  ISSUES=$((ISSUES + 1))
fi

if [ -x "$SKILL_DIR/scripts/chunk-diff.sh" ]; then
  echo -e "${GREEN}✓${NC} chunk-diff.sh is executable"
else
  echo -e "${YELLOW}⚠${NC} chunk-diff.sh is not executable"
  echo "  Run: chmod +x $SKILL_DIR/scripts/chunk-diff.sh"
  ISSUES=$((ISSUES + 1))
fi

if [ -x "$SKILL_DIR/scripts/review-helper.sh" ]; then
  echo -e "${GREEN}✓${NC} review-helper.sh is executable"
else
  echo -e "${YELLOW}⚠${NC} review-helper.sh is not executable"
  echo "  Run: chmod +x $SKILL_DIR/scripts/review-helper.sh"
  ISSUES=$((ISSUES + 1))
fi

if [ -x "$SKILL_DIR/scripts/comment-manager.sh" ]; then
  echo -e "${GREEN}✓${NC} comment-manager.sh is executable"
else
  echo -e "${YELLOW}⚠${NC} comment-manager.sh is not executable"
  echo "  Run: chmod +x $SKILL_DIR/scripts/comment-manager.sh"
  ISSUES=$((ISSUES + 1))
fi

echo ""
echo "5. Validating SKILL.md Frontmatter"
echo "-----------------------------------"

if [ -f "$SKILL_DIR/SKILL.md" ]; then
  # Check for required frontmatter fields
  if grep -q "^name: github-pr-manager" "$SKILL_DIR/SKILL.md"; then
    echo -e "${GREEN}✓${NC} Name field present"
  else
    echo -e "${RED}✗${NC} Name field missing or incorrect"
    ISSUES=$((ISSUES + 1))
  fi

  if grep -q "^description:" "$SKILL_DIR/SKILL.md"; then
    echo -e "${GREEN}✓${NC} Description field present"
  else
    echo -e "${RED}✗${NC} Description field missing"
    ISSUES=$((ISSUES + 1))
  fi

  if grep -q "^allowed-tools:" "$SKILL_DIR/SKILL.md"; then
    echo -e "${GREEN}✓${NC} Allowed-tools field present"
  else
    echo -e "${YELLOW}⚠${NC} Allowed-tools field missing (optional)"
  fi

  # Check frontmatter syntax
  if grep -q "^---$" "$SKILL_DIR/SKILL.md"; then
    echo -e "${GREEN}✓${NC} Frontmatter delimiters present"
  else
    echo -e "${RED}✗${NC} Frontmatter delimiters missing or malformed"
    ISSUES=$((ISSUES + 1))
  fi
fi

echo ""
echo "========================================"
echo "Verification Summary"
echo "========================================"

if [ $ISSUES -eq 0 ]; then
  echo -e "${GREEN}✓ All checks passed!${NC}"
  echo ""
  echo "The GitHub PR Manager skill is properly installed and ready to use."
  echo ""
  echo "Next steps:"
  echo "1. Start Claude Code: claude"
  echo "2. Ask Claude: 'What skills do I have?'"
  echo "3. Try: 'Review PR #123 in owner/repo'"
  echo ""
  exit 0
else
  echo -e "${YELLOW}⚠ Found $ISSUES issue(s)${NC}"
  echo ""
  echo "Please address the issues above before using the skill."
  echo ""
  echo "Common fixes:"
  echo "- Install GitHub CLI: https://cli.github.com/"
  echo "- Authenticate: gh auth login"
  echo "- Fix permissions: chmod +x .claude/skills/github-pr-manager/scripts/*.sh"
  echo "- Install jq: sudo apt install jq (Linux) or brew install jq (macOS)"
  echo ""
  exit 1
fi
