# GitHub PR Operations - Complete Reference

This document provides comprehensive details on all GitHub CLI operations for PR management, including advanced options, JSON output formats, and API integration patterns.

## Table of Contents

1. [Authentication & Setup](#authentication--setup)
2. [PR Information Commands](#pr-information-commands)
3. [PR Diff Commands](#pr-diff-commands)
4. [PR Comment Commands](#pr-comment-commands)
5. [PR Review Commands](#pr-review-commands)
6. [PR Lifecycle Commands](#pr-lifecycle-commands)
7. [API Integration](#api-integration)
8. [Rate Limiting & Performance](#rate-limiting--performance)
9. [Advanced Patterns](#advanced-patterns)

---

## Authentication & Setup

### Initial Authentication

```bash
# Interactive authentication
gh auth login

# Token authentication
gh auth login --with-token < token.txt

# Authenticate with specific scopes
gh auth login --scopes "repo,read:org,write:discussion"

# Check current authentication
gh auth status

# View token scopes
gh auth status -t
```

### Configuration

```bash
# Set default repository
gh repo set-default <OWNER/REPO>

# Configure defaults
gh config set editor vim
gh config set pager less
gh config set prompt enabled

# View all config
gh config list
```

---

## PR Information Commands

### Basic PR Viewing

```bash
# View PR in terminal
gh pr view <PR_NUMBER>

# View PR in browser
gh pr view <PR_NUMBER> --web

# View with specific repository
gh pr view <PR_NUMBER> --repo <OWNER/REPO>

# View comments
gh pr view <PR_NUMBER> --comments
```

### JSON Output for Parsing

```bash
# Get all PR data
gh pr view <PR_NUMBER> --json \
  title,body,state,number,author,createdAt,updatedAt,\
  additions,deletions,changedFiles,mergeable,mergeStateStatus,\
  commits,reviews,labels,milestone,assignees

# Specific fields only
gh pr view <PR_NUMBER> --json title,additions,deletions

# Parse with jq
gh pr view <PR_NUMBER> --json title,state | jq '.title'
```

### Available JSON Fields

```json
{
  "additions": 150,
  "assignees": [{"login": "username"}],
  "author": {"login": "author_name"},
  "autoMergeRequest": null,
  "baseRefName": "main",
  "body": "PR description",
  "changedFiles": 12,
  "closed": false,
  "closedAt": null,
  "comments": [{"body": "comment text"}],
  "commits": [{"oid": "abc123"}],
  "createdAt": "2025-01-13T00:00:00Z",
  "deletions": 50,
  "files": [{"path": "src/file.js", "additions": 10}],
  "headRefName": "feature-branch",
  "headRepository": {"name": "repo"},
  "headRepositoryOwner": {"login": "owner"},
  "id": "PR_kwDOABC123",
  "isCrossRepository": false,
  "isDraft": false,
  "labels": [{"name": "bug"}],
  "latestReviews": [{"state": "APPROVED"}],
  "maintainerCanModify": true,
  "mergeCommit": null,
  "mergeStateStatus": "CLEAN",
  "mergeable": "MERGEABLE",
  "mergedAt": null,
  "mergedBy": null,
  "milestone": {"title": "v1.0"},
  "number": 123,
  "potentialMergeCommit": null,
  "projectCards": [],
  "reactionGroups": [],
  "reviewDecision": "APPROVED",
  "reviewRequests": [],
  "reviews": [{"state": "APPROVED", "author": {"login": "reviewer"}}],
  "state": "OPEN",
  "statusCheckRollup": [{"state": "SUCCESS"}],
  "title": "Fix authentication bug",
  "updatedAt": "2025-01-13T12:00:00Z",
  "url": "https://github.com/owner/repo/pull/123"
}
```

### List PRs

```bash
# List open PRs
gh pr list

# List all PRs (including closed)
gh pr list --state all

# Filter by author
gh pr list --author <USERNAME>

# Filter by label
gh pr list --label bug

# Filter by assignee
gh pr list --assignee <USERNAME>

# Limit results
gh pr list --limit 50

# Search PRs
gh pr list --search "fix auth"

# JSON output
gh pr list --json number,title,author,state,createdAt
```

---

## PR Diff Commands

### Basic Diff Operations

```bash
# View entire PR diff
gh pr diff <PR_NUMBER>

# View specific file
gh pr diff <PR_NUMBER> -- <FILE_PATH>

# View multiple files
gh pr diff <PR_NUMBER> -- <FILE1> <FILE2>

# View directory
gh pr diff <PR_NUMBER> -- src/

# Name only (list changed files)
gh pr diff <PR_NUMBER> --name-only

# Name and status
gh pr diff <PR_NUMBER> --name-status
```

### Diff Filtering

```bash
# Only added files
gh pr diff <PR_NUMBER> --diff-filter=A

# Only modified files
gh pr diff <PR_NUMBER> --diff-filter=M

# Only deleted files
gh pr diff <PR_NUMBER> --diff-filter=D

# Only renamed files
gh pr diff <PR_NUMBER> --diff-filter=R

# Combined filters (added or modified)
gh pr diff <PR_NUMBER> --diff-filter=AM

# Exclude files
gh pr diff <PR_NUMBER> ':(exclude)*.md'
```

### Diff Format Options

```bash
# Patch format
gh pr diff <PR_NUMBER> --patch

# Unified diff with custom context lines
git diff -U5  # 5 lines of context (when checked out)

# Color options
gh pr diff <PR_NUMBER> --color=always
gh pr diff <PR_NUMBER> --color=never

# Statistics only
git diff --stat origin/main...HEAD
```

### Advanced Diff Operations

```bash
# Diff specific commit range
gh api repos/<OWNER>/<REPO>/compare/BASE...HEAD

# Get file content at specific commit
gh api repos/<OWNER>/<REPO>/contents/<FILE>?ref=<COMMIT>

# Get raw diff via API
gh api repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/files
```

---

## PR Comment Commands

### Basic Commenting

```bash
# Add general comment
gh pr comment <PR_NUMBER> --body "Great work!"

# Comment from file
gh pr comment <PR_NUMBER> --body-file comment.txt

# Comment from stdin
echo "LGTM" | gh pr comment <PR_NUMBER> --body-file -

# Edit existing comment
gh pr comment <PR_NUMBER> --edit-last
```

### Inline Comments (via API)

GitHub CLI doesn't directly support inline comments on specific lines, but you can use the API:

```bash
# Add inline comment
gh api \
  --method POST \
  repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/comments \
  -f body='Consider using const here' \
  -f commit_id='<COMMIT_SHA>' \
  -f path='src/file.js' \
  -F line=42

# Reply to comment
gh api \
  --method POST \
  repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/comments \
  -f body='Good point, will fix' \
  -F in_reply_to=<COMMENT_ID>
```

### Comment Management

```bash
# List all comments
gh api repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/comments

# List review comments
gh pr view <PR_NUMBER> --json comments --jq '.comments[]'

# Delete comment (requires comment ID)
gh api \
  --method DELETE \
  repos/<OWNER>/<REPO>/pulls/comments/<COMMENT_ID>

# Update comment
gh api \
  --method PATCH \
  repos/<OWNER>/<REPO>/pulls/comments/<COMMENT_ID> \
  -f body='Updated comment text'
```

---

## PR Review Commands

### Submit Review

```bash
# Approve PR
gh pr review <PR_NUMBER> --approve

# Approve with comment
gh pr review <PR_NUMBER> --approve --body "LGTM! Great implementation."

# Request changes
gh pr review <PR_NUMBER> --request-changes --body "Please address these issues..."

# Comment only (no approval/rejection)
gh pr review <PR_NUMBER> --comment --body "Some observations..."
```

### Review with Comments File

```bash
# Create review with detailed feedback
gh pr review <PR_NUMBER> --request-changes --body-file - <<EOF
# Review Summary

Found several issues that need addressing:

## Security
- Line 42 in auth.js: SQL injection vulnerability
- Line 156 in api.js: Missing input validation

## Performance
- Line 78 in utils.js: Inefficient loop, consider using map()

## Tests
- Missing test coverage for new authentication flow

Please address these before merging.
EOF
```

### Review via API (with inline comments)

```bash
# Start a review
REVIEW_ID=$(gh api \
  --method POST \
  repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/reviews \
  -f body='Starting review' \
  -f event='PENDING' \
  --jq '.id')

# Add inline comments to the review
gh api \
  --method POST \
  repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/comments \
  -f body='Consider refactoring this' \
  -f commit_id='<COMMIT_SHA>' \
  -f path='src/file.js' \
  -F line=42 \
  -F pull_request_review_id=$REVIEW_ID

# Submit the review
gh api \
  --method POST \
  repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/reviews/$REVIEW_ID/events \
  -f event='REQUEST_CHANGES' \
  -f body='Please address the inline comments'
```

### List Reviews

```bash
# View all reviews
gh pr view <PR_NUMBER> --json reviews --jq '.reviews[]'

# Filter by state
gh api repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/reviews \
  --jq '.[] | select(.state=="APPROVED")'

# Get latest review from each reviewer
gh pr view <PR_NUMBER> --json latestReviews
```

---

## PR Lifecycle Commands

### Checkout & Testing

```bash
# Checkout PR locally
gh pr checkout <PR_NUMBER>

# Checkout with specific branch name
gh pr checkout <PR_NUMBER> --branch my-review-branch

# Checkout and rebase
gh pr checkout <PR_NUMBER>
git rebase main
```

### PR Status & Checks

```bash
# View CI/CD checks
gh pr checks <PR_NUMBER>

# Watch checks in real-time
gh pr checks <PR_NUMBER> --watch

# View specific check
gh pr checks <PR_NUMBER> --check "Build"

# Get check status via API
gh api repos/<OWNER>/<REPO>/commits/<COMMIT_SHA>/check-runs
```

### Merge Operations

```bash
# Merge with commit
gh pr merge <PR_NUMBER>

# Merge with squash
gh pr merge <PR_NUMBER> --squash

# Merge with rebase
gh pr merge <PR_NUMBER> --rebase

# Auto-merge when checks pass
gh pr merge <PR_NUMBER> --auto

# Delete branch after merge
gh pr merge <PR_NUMBER> --delete-branch

# Merge with custom message
gh pr merge <PR_NUMBER> --body "Closes #123"
```

### Close & Reopen

```bash
# Close PR
gh pr close <PR_NUMBER>

# Close with comment
gh pr close <PR_NUMBER> --comment "Closing due to..."

# Reopen PR
gh pr reopen <PR_NUMBER>
```

### Draft Status

```bash
# Mark as ready for review
gh pr ready <PR_NUMBER>

# Convert to draft
gh pr ready <PR_NUMBER> --undo
```

---

## API Integration

### Direct API Access

```bash
# Generic API call
gh api <ENDPOINT> [flags]

# Common endpoints
gh api repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>
gh api repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/files
gh api repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/commits
gh api repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/comments
gh api repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/reviews

# With pagination
gh api --paginate repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/files

# POST request
gh api --method POST <ENDPOINT> -f field=value

# PATCH request
gh api --method PATCH <ENDPOINT> -f field=value

# DELETE request
gh api --method DELETE <ENDPOINT>
```

### GraphQL Queries

```bash
# Execute GraphQL query
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        title
        body
        files(first: 100) {
          nodes {
            path
            additions
            deletions
          }
        }
      }
    }
  }
' -f owner=<OWNER> -f repo=<REPO> -F number=<PR_NUMBER>

# Save query to file
gh api graphql -F query=@query.graphql -f owner=<OWNER>
```

### Batch Operations

```bash
# Process multiple PRs
for pr in $(gh pr list --json number --jq '.[].number'); do
  gh pr view $pr --json title,state
done

# Bulk approve (use with caution!)
gh pr list --label "auto-approve" --json number --jq '.[].number' | \
  xargs -I {} gh pr review {} --approve
```

---

## Rate Limiting & Performance

### Check Rate Limits

```bash
# View rate limit status
gh api rate_limit

# Parse specific limits
gh api rate_limit --jq '.rate.remaining'
gh api rate_limit --jq '.rate.reset' | xargs -I {} date -d @{}
```

### Rate Limit Details

```json
{
  "resources": {
    "core": {
      "limit": 5000,
      "remaining": 4999,
      "reset": 1700000000,
      "used": 1
    },
    "search": {
      "limit": 30,
      "remaining": 30,
      "reset": 1700000000,
      "used": 0
    },
    "graphql": {
      "limit": 5000,
      "remaining": 5000,
      "reset": 1700000000,
      "used": 0
    }
  }
}
```

### Optimization Strategies

1. **Use GraphQL for Complex Queries**
```bash
# REST API: 3 requests
gh pr view <PR_NUMBER>
gh pr view <PR_NUMBER> --json files
gh pr view <PR_NUMBER> --json reviews

# GraphQL: 1 request
gh api graphql -f query='...' # Fetch all data at once
```

2. **Batch Requests**
```bash
# Inefficient: N requests
for file in $(gh pr diff <PR_NUMBER> --name-only); do
  gh pr diff <PR_NUMBER> -- $file
done

# Efficient: 1 request
gh api repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/files --paginate
```

3. **Cache Results**
```bash
# Cache PR data
gh pr view <PR_NUMBER> --json title,files > pr_cache.json

# Use cached data
jq '.files[] | .path' pr_cache.json
```

---

## Advanced Patterns

### Pattern 1: Automated Review Workflow

```bash
#!/bin/bash
# auto-review.sh

PR_NUMBER=$1
REPO=$2

# Get PR info
PR_DATA=$(gh pr view $PR_NUMBER --repo $REPO --json title,files,additions,deletions)

# Analyze complexity
ADDITIONS=$(echo $PR_DATA | jq '.additions')
FILES=$(echo $PR_DATA | jq '.files | length')

# Auto-approve simple PRs
if [ $ADDITIONS -lt 50 ] && [ $FILES -lt 3 ]; then
  gh pr review $PR_NUMBER --approve --body "Auto-approved: Small change"
  exit 0
fi

# Request manual review for complex PRs
gh pr comment $PR_NUMBER --body "This PR requires manual review (${ADDITIONS} additions, ${FILES} files)"
```

### Pattern 2: Chunked Diff Processing

```bash
#!/bin/bash
# chunk-diff.sh

PR_NUMBER=$1
CHUNK_SIZE=50  # Lines per chunk

# Get all changed files
FILES=$(gh pr diff $PR_NUMBER --name-only)

for file in $FILES; do
  echo "Processing: $file"

  # Get file diff
  DIFF=$(gh pr diff $PR_NUMBER -- $file)

  # Count lines
  LINES=$(echo "$DIFF" | wc -l)

  if [ $LINES -gt $CHUNK_SIZE ]; then
    echo "  Large file ($LINES lines), processing in chunks..."

    # Split into chunks
    echo "$DIFF" | split -l $CHUNK_SIZE - chunk_

    # Process each chunk
    for chunk in chunk_*; do
      echo "  Processing chunk: $chunk"
      # Your processing logic here
      cat $chunk
    done

    rm chunk_*
  else
    echo "  Small file, processing entire diff"
    echo "$DIFF"
  fi
done
```

### Pattern 3: Context-Aware Comments

```bash
#!/bin/bash
# smart-comment.sh

PR_NUMBER=$1
FILE_PATH=$2
LINE_NUMBER=$3
COMMENT=$4

# Get commit SHA
COMMIT_SHA=$(gh pr view $PR_NUMBER --json commits --jq '.commits[-1].oid')

# Verify line exists in diff
gh pr diff $PR_NUMBER -- $FILE_PATH | grep -n "^[+-]" | grep "^${LINE_NUMBER}:"

if [ $? -eq 0 ]; then
  # Line exists, add comment
  gh api \
    --method POST \
    repos/$(gh repo view --json nameWithOwner --jq .nameWithOwner)/pulls/${PR_NUMBER}/comments \
    -f body="$COMMENT" \
    -f commit_id="$COMMIT_SHA" \
    -f path="$FILE_PATH" \
    -F line=$LINE_NUMBER
else
  echo "Error: Line $LINE_NUMBER not in diff for $FILE_PATH"
  exit 1
fi
```

### Pattern 4: Review Statistics

```bash
#!/bin/bash
# review-stats.sh

REPO=$1

# Get all PRs
PRS=$(gh pr list --repo $REPO --state all --limit 100 --json number,reviews)

# Calculate statistics
echo "Review Statistics:"
echo "=================="

TOTAL=$(echo $PRS | jq '. | length')
echo "Total PRs: $TOTAL"

APPROVED=$(echo $PRS | jq '[.[] | select(.reviews[]?.state=="APPROVED")] | length')
echo "Approved: $APPROVED"

CHANGES_REQUESTED=$(echo $PRS | jq '[.[] | select(.reviews[]?.state=="CHANGES_REQUESTED")] | length')
echo "Changes Requested: $CHANGES_REQUESTED"

NO_REVIEWS=$(echo $PRS | jq '[.[] | select(.reviews | length == 0)] | length')
echo "No Reviews: $NO_REVIEWS"

# Average reviews per PR
AVG_REVIEWS=$(echo $PRS | jq '[.[] | .reviews | length] | add / length')
echo "Average Reviews/PR: $AVG_REVIEWS"
```

### Pattern 5: Large PR Navigation Helper

```bash
#!/bin/bash
# navigate-pr.sh

PR_NUMBER=$1

# Get PR metadata
PR_JSON=$(gh pr view $PR_NUMBER --json files,additions,deletions)

FILES=$(echo $PR_JSON | jq '.files | length')
ADDITIONS=$(echo $PR_JSON | jq '.additions')
DELETIONS=$(echo $PR_JSON | jq '.deletions')

echo "PR #$PR_NUMBER Overview"
echo "======================"
echo "Files changed: $FILES"
echo "Lines added: $ADDITIONS"
echo "Lines deleted: $DELETIONS"
echo ""

# Categorize files
echo "File Categories:"
echo "----------------"

echo "Critical files (security, auth):"
echo $PR_JSON | jq -r '.files[] | select(.path | test("auth|security|password|token")) | "  - \(.path) (+\(.additions)/-\(.deletions))"'

echo ""
echo "Core functionality:"
echo $PR_JSON | jq -r '.files[] | select(.path | test("src/.*\\.js$|lib/")) | "  - \(.path) (+\(.additions)/-\(.deletions))"'

echo ""
echo "Tests:"
echo $PR_JSON | jq -r '.files[] | select(.path | test("test|spec|\\.test\\.|_test\\.")) | "  - \(.path) (+\(.additions)/-\(.deletions))"'

echo ""
echo "Documentation:"
echo $PR_JSON | jq -r '.files[] | select(.path | test("\\.md$|docs/")) | "  - \(.path) (+\(.additions)/-\(.deletions))"'

# Suggest review order
echo ""
echo "Suggested Review Order:"
echo "----------------------"
echo "1. Review critical files first"
echo "2. Check core functionality changes"
echo "3. Verify test coverage"
echo "4. Review documentation updates"
```

---

## Troubleshooting

### Common Errors

1. **"Pull request not found"**
```bash
# Verify PR exists
gh pr list --limit 100 | grep <PR_NUMBER>

# Check repository
gh repo view
```

2. **"Resource not accessible by integration"**
```bash
# Re-authenticate with proper scopes
gh auth login --scopes "repo,read:org"
```

3. **"Bad credentials"**
```bash
# Refresh authentication
gh auth refresh
```

4. **"API rate limit exceeded"**
```bash
# Check reset time
gh api rate_limit --jq '.rate.reset' | xargs -I {} date -d @{}

# Wait or use personal token
gh auth login --with-token < token.txt
```

### Debug Mode

```bash
# Enable debug output
export GH_DEBUG=1
gh pr view <PR_NUMBER>

# Or per-command
GH_DEBUG=1 gh pr view <PR_NUMBER>

# Verbose HTTP logging
GH_DEBUG=api gh pr view <PR_NUMBER>
```

---

## References

- GitHub CLI Documentation: https://cli.github.com/manual/
- GitHub REST API: https://docs.github.com/en/rest
- GitHub GraphQL API: https://docs.github.com/en/graphql
- Pull Requests API: https://docs.github.com/en/rest/pulls

---

## Summary

This reference covers:
- ✅ All major GitHub CLI PR operations
- ✅ JSON parsing and data extraction
- ✅ API integration patterns
- ✅ Rate limiting strategies
- ✅ Advanced automation workflows
- ✅ Error handling and debugging

Use this as a comprehensive guide for implementing PR management features with proper error handling, performance optimization, and scalability.
