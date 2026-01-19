#!/bin/bash
# comment-manager.sh - Manage PR comments and reviews
# Usage: ./comment-manager.sh <COMMAND> <PR_NUMBER> <REPO> [ARGS...]

set -e

COMMAND=$1
PR_NUMBER=$2
REPO=$3

usage() {
  cat <<EOF
Usage: ./comment-manager.sh <COMMAND> <PR_NUMBER> <REPO> [ARGS...]

Commands:
  list                     List all comments on PR
  add <TEXT>              Add general comment
  add-inline <FILE> <LINE> <TEXT>
                          Add inline comment on specific line
  reply <COMMENT_ID> <TEXT>
                          Reply to existing comment
  edit <COMMENT_ID> <TEXT>
                          Edit existing comment
  delete <COMMENT_ID>     Delete comment
  resolve <COMMENT_ID>    Resolve comment thread

Examples:
  ./comment-manager.sh list 123 owner/repo
  ./comment-manager.sh add 123 owner/repo "Great work!"
  ./comment-manager.sh add-inline 123 owner/repo src/file.js 42 "Consider refactoring"
  ./comment-manager.sh reply 123 owner/repo 456789 "Good point, will fix"
  ./comment-manager.sh delete 123 owner/repo 456789

EOF
  exit 1
}

if [ -z "$COMMAND" ] || [ -z "$PR_NUMBER" ] || [ -z "$REPO" ]; then
  usage
fi

case $COMMAND in
  list)
    echo "Comments on PR #$PR_NUMBER:"
    echo "========================================"

    # Get all comments
    gh api "repos/$REPO/pulls/$PR_NUMBER/comments" \
      --jq '.[] | "ID: \(.id)\nAuthor: @\(.user.login)\nFile: \(.path):\(.line // "N/A")\nCreated: \(.created_at)\nBody: \(.body)\n---"'

    echo ""
    echo "Review comments:"
    echo "========================================"

    gh pr view $PR_NUMBER --repo $REPO --json reviews \
      --jq '.reviews[] | "Author: @\(.author.login)\nState: \(.state)\nBody: \(.body)\nCreated: \(.submittedAt)\n---"'
    ;;

  add)
    TEXT=$4
    if [ -z "$TEXT" ]; then
      echo "Error: Comment text required"
      usage
    fi

    echo "Adding comment to PR #$PR_NUMBER..."
    gh pr comment $PR_NUMBER --repo $REPO --body "$TEXT"
    echo "✓ Comment added"
    ;;

  add-inline)
    FILE=$4
    LINE=$5
    TEXT=$6

    if [ -z "$FILE" ] || [ -z "$LINE" ] || [ -z "$TEXT" ]; then
      echo "Error: File path, line number, and comment text required"
      usage
    fi

    echo "Adding inline comment to $FILE:$LINE..."

    # Get latest commit SHA
    COMMIT_SHA=$(gh pr view $PR_NUMBER --repo $REPO --json commits --jq '.commits[-1].oid')

    # Add comment via API
    gh api \
      --method POST \
      "repos/$REPO/pulls/$PR_NUMBER/comments" \
      -f body="$TEXT" \
      -f commit_id="$COMMIT_SHA" \
      -f path="$FILE" \
      -F line=$LINE

    echo "✓ Inline comment added"
    ;;

  reply)
    COMMENT_ID=$4
    TEXT=$5

    if [ -z "$COMMENT_ID" ] || [ -z "$TEXT" ]; then
      echo "Error: Comment ID and reply text required"
      usage
    fi

    echo "Replying to comment #$COMMENT_ID..."

    gh api \
      --method POST \
      "repos/$REPO/pulls/$PR_NUMBER/comments" \
      -f body="$TEXT" \
      -F in_reply_to=$COMMENT_ID

    echo "✓ Reply added"
    ;;

  edit)
    COMMENT_ID=$4
    TEXT=$5

    if [ -z "$COMMENT_ID" ] || [ -z "$TEXT" ]; then
      echo "Error: Comment ID and new text required"
      usage
    fi

    echo "Editing comment #$COMMENT_ID..."

    gh api \
      --method PATCH \
      "repos/$REPO/pulls/comments/$COMMENT_ID" \
      -f body="$TEXT"

    echo "✓ Comment updated"
    ;;

  delete)
    COMMENT_ID=$4

    if [ -z "$COMMENT_ID" ]; then
      echo "Error: Comment ID required"
      usage
    fi

    read -p "Delete comment #$COMMENT_ID? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      echo "Cancelled"
      exit 0
    fi

    echo "Deleting comment #$COMMENT_ID..."

    gh api \
      --method DELETE \
      "repos/$REPO/pulls/comments/$COMMENT_ID"

    echo "✓ Comment deleted"
    ;;

  resolve)
    COMMENT_ID=$4

    if [ -z "$COMMENT_ID" ]; then
      echo "Error: Comment ID required"
      usage
    fi

    echo "Resolving comment thread #$COMMENT_ID..."

    # GitHub doesn't have direct API for resolving, but we can add a reply
    gh api \
      --method POST \
      "repos/$REPO/pulls/$PR_NUMBER/comments" \
      -f body="✓ Resolved" \
      -F in_reply_to=$COMMENT_ID

    echo "✓ Added resolution marker"
    ;;

  *)
    echo "Error: Unknown command '$COMMAND'"
    usage
    ;;
esac
