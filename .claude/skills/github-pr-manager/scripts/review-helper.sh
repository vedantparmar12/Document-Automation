#!/bin/bash
# review-helper.sh - Interactive PR review helper
# Usage: ./review-helper.sh <PR_NUMBER> <REPO>

set -e

PR_NUMBER=$1
REPO=$2

if [ -z "$PR_NUMBER" ] || [ -z "$REPO" ]; then
  echo "Usage: ./review-helper.sh <PR_NUMBER> <REPO>"
  echo "Example: ./review-helper.sh 123 owner/repo"
  exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}PR Review Helper${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get PR information
echo "Fetching PR information..."
PR_JSON=$(gh pr view $PR_NUMBER --repo $REPO --json title,body,author,additions,deletions,changedFiles,state,isDraft)

TITLE=$(echo "$PR_JSON" | jq -r '.title')
AUTHOR=$(echo "$PR_JSON" | jq -r '.author.login')
STATE=$(echo "$PR_JSON" | jq -r '.state')
IS_DRAFT=$(echo "$PR_JSON" | jq -r '.isDraft')
ADDITIONS=$(echo "$PR_JSON" | jq -r '.additions')
DELETIONS=$(echo "$PR_JSON" | jq -r '.deletions')
FILES=$(echo "$PR_JSON" | jq -r '.changedFiles')

echo ""
echo -e "${GREEN}Title:${NC} $TITLE"
echo -e "${GREEN}Author:${NC} @$AUTHOR"
echo -e "${GREEN}State:${NC} $STATE"
echo -e "${GREEN}Draft:${NC} $IS_DRAFT"
echo -e "${GREEN}Changes:${NC} +$ADDITIONS / -$DELETIONS"
echo -e "${GREEN}Files:${NC} $FILES"
echo ""

# Check if draft
if [ "$IS_DRAFT" = "true" ]; then
  echo -e "${YELLOW}⚠️  This is a draft PR. Review when marked as ready.${NC}"
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
  fi
fi

# Complexity assessment
TOTAL_CHANGES=$((ADDITIONS + DELETIONS))

if [ $TOTAL_CHANGES -lt 100 ]; then
  COMPLEXITY="${GREEN}LOW${NC}"
  STRATEGY="Quick review - all files at once"
elif [ $TOTAL_CHANGES -lt 500 ]; then
  COMPLEXITY="${YELLOW}MEDIUM${NC}"
  STRATEGY="Standard review - by category"
else
  COMPLEXITY="${RED}HIGH${NC}"
  STRATEGY="Phased review - multiple sessions"
fi

echo -e "${GREEN}Complexity:${NC} $COMPLEXITY ($TOTAL_CHANGES lines)"
echo -e "${GREEN}Strategy:${NC} $STRATEGY"
echo ""

# Create review workspace
WORKSPACE=$(mktemp -d)
echo "Review workspace: $WORKSPACE"
echo ""

# Get changed files
echo "Fetching changed files..."
gh pr diff $PR_NUMBER --repo $REPO --name-status > "$WORKSPACE/files.txt"

# Categorize files
echo "Categorizing files..."

grep -iE "(auth|security|password|token|crypto|payment|billing)" "$WORKSPACE/files.txt" > "$WORKSPACE/critical.txt" 2>/dev/null || true
grep -iE "\\.(test|spec)\\." "$WORKSPACE/files.txt" > "$WORKSPACE/tests.txt" 2>/dev/null || true
grep -iE "\\.(md|txt|rst)$|docs/" "$WORKSPACE/files.txt" > "$WORKSPACE/docs.txt" 2>/dev/null || true
grep -iE "\\.(json|ya?ml|toml|ini)$|config" "$WORKSPACE/files.txt" > "$WORKSPACE/config.txt" 2>/dev/null || true

CRITICAL_COUNT=$(wc -l < "$WORKSPACE/critical.txt")
TEST_COUNT=$(wc -l < "$WORKSPACE/tests.txt")
DOC_COUNT=$(wc -l < "$WORKSPACE/docs.txt")
CONFIG_COUNT=$(wc -l < "$WORKSPACE/config.txt")

echo ""
echo -e "${RED}🔴 Critical files:${NC} $CRITICAL_COUNT"
echo -e "${GREEN}🧪 Test files:${NC} $TEST_COUNT"
echo -e "${BLUE}📄 Documentation:${NC} $DOC_COUNT"
echo -e "${YELLOW}⚙️  Configuration:${NC} $CONFIG_COUNT"
echo ""

# Review menu
while true; do
  echo "========================================="
  echo "Review Options:"
  echo "========================================="
  echo "1) View PR description"
  echo "2) List all changed files"
  echo "3) View critical files"
  echo "4) View specific file diff"
  echo "5) View test files"
  echo "6) Check CI status"
  echo "7) Add comment"
  echo "8) Submit review (approve)"
  echo "9) Submit review (request changes)"
  echo "10) Submit review (comment only)"
  echo "11) Open PR in browser"
  echo "12) Run analysis script"
  echo "q) Quit"
  echo ""
  read -p "Choose option: " option

  case $option in
    1)
      echo ""
      echo "========================================="
      gh pr view $PR_NUMBER --repo $REPO
      echo "========================================="
      echo ""
      ;;

    2)
      echo ""
      echo "Changed files:"
      cat "$WORKSPACE/files.txt"
      echo ""
      ;;

    3)
      if [ $CRITICAL_COUNT -gt 0 ]; then
        echo ""
        echo -e "${RED}Critical files that need careful review:${NC}"
        cat "$WORKSPACE/critical.txt"
        echo ""
        read -p "Review a critical file? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
          read -p "Enter file path: " filepath
          echo ""
          gh pr diff $PR_NUMBER --repo $REPO -- "$filepath" | less
        fi
      else
        echo ""
        echo "No critical files identified."
        echo ""
      fi
      ;;

    4)
      echo ""
      read -p "Enter file path: " filepath
      echo ""
      gh pr diff $PR_NUMBER --repo $REPO -- "$filepath" | less
      echo ""
      ;;

    5)
      if [ $TEST_COUNT -gt 0 ]; then
        echo ""
        echo "Test files:"
        cat "$WORKSPACE/tests.txt"
        echo ""
        read -p "Review a test file? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
          read -p "Enter file path: " filepath
          echo ""
          gh pr diff $PR_NUMBER --repo $REPO -- "$filepath" | less
        fi
      else
        echo ""
        echo -e "${YELLOW}⚠️  No test files modified!${NC}"
        echo ""
      fi
      ;;

    6)
      echo ""
      echo "CI/CD Status:"
      gh pr checks $PR_NUMBER --repo $REPO
      echo ""
      ;;

    7)
      echo ""
      echo "Add comment to PR"
      read -p "Comment text: " comment
      gh pr comment $PR_NUMBER --repo $REPO --body "$comment"
      echo -e "${GREEN}✓ Comment added${NC}"
      echo ""
      ;;

    8)
      echo ""
      echo "Approve PR"
      read -p "Approval message (optional): " message
      if [ -z "$message" ]; then
        gh pr review $PR_NUMBER --repo $REPO --approve
      else
        gh pr review $PR_NUMBER --repo $REPO --approve --body "$message"
      fi
      echo -e "${GREEN}✓ PR approved${NC}"
      echo ""
      ;;

    9)
      echo ""
      echo "Request changes"
      echo "Enter feedback (Ctrl+D when done):"
      feedback=$(cat)
      echo "$feedback" | gh pr review $PR_NUMBER --repo $REPO --request-changes --body-file -
      echo -e "${YELLOW}✓ Changes requested${NC}"
      echo ""
      ;;

    10)
      echo ""
      echo "Comment on PR (no approval/rejection)"
      echo "Enter comment (Ctrl+D when done):"
      comment=$(cat)
      echo "$comment" | gh pr review $PR_NUMBER --repo $REPO --comment --body-file -
      echo -e "${BLUE}✓ Review comment added${NC}"
      echo ""
      ;;

    11)
      echo ""
      gh pr view $PR_NUMBER --repo $REPO --web
      echo ""
      ;;

    12)
      echo ""
      # Check if analyze-pr.py exists
      SCRIPT_DIR="$(dirname "$0")"
      if [ -f "$SCRIPT_DIR/analyze-pr.py" ]; then
        python3 "$SCRIPT_DIR/analyze-pr.py" $PR_NUMBER $REPO
      else
        echo -e "${RED}Error: analyze-pr.py not found${NC}"
      fi
      echo ""
      ;;

    q|Q)
      echo ""
      echo "Cleaning up workspace..."
      rm -rf "$WORKSPACE"
      echo "Review session ended."
      exit 0
      ;;

    *)
      echo ""
      echo -e "${RED}Invalid option${NC}"
      echo ""
      ;;
  esac
done
