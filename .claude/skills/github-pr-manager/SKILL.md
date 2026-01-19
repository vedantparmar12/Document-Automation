---
name: github-pr-manager
description: Manage GitHub pull requests with smart navigation, code review, and commenting capabilities. Use when working with PRs, reviewing code changes, adding PR comments, navigating large diffs, or performing code reviews on GitHub. Handles context management for large PRs automatically.
allowed-tools:
  - Read
  - Bash(gh:*)
  - Bash(git:*)
  - Grep
  - Glob
  - Write
  - Edit
user-invocable: true
---

# GitHub PR Manager Skill

Enables intelligent interaction with GitHub pull requests directly from Claude CLI. This skill handles reading PRs, navigating large changesets, adding contextual comments, and performing comprehensive code reviews while managing context window limitations automatically.

## Core Capabilities

1. **PR Reading & Analysis**: Fetch and analyze PR metadata, descriptions, and file changes
2. **Smart Navigation**: Handle PRs with 100+ files through intelligent chunking
3. **Inline Commenting**: Add contextual comments to specific code lines
4. **Code Review**: Perform structured reviews with approval/change requests
5. **Context Management**: Automatically chunk large diffs to prevent token overflow

## Prerequisites

Before using this skill, ensure:

```bash
# GitHub CLI must be installed and authenticated
gh --version

# Authenticate if needed
gh auth login

# Verify authentication
gh auth status
```

## Quick Start

### 1. Reading a Pull Request

To get an overview of a PR:

```bash
gh pr view <PR_NUMBER> --repo <OWNER/REPO>
```

I will automatically:
- Parse the PR title, description, and metadata
- Identify all changed files
- Estimate the size and complexity
- Suggest navigation strategy for large PRs

### 2. Listing Changed Files

```bash
gh pr diff <PR_NUMBER> --repo <OWNER/REPO> --name-only
```

This shows all files changed in the PR, which I'll organize by:
- Directory structure
- File type
- Change size (additions/deletions)

### 3. Reading Specific File Changes

For manageable files:
```bash
gh pr diff <PR_NUMBER> --repo <OWNER/REPO> -- <FILE_PATH>
```

For large files (>500 lines), I will:
- Chunk the diff into logical sections
- Preserve context between chunks
- Maintain line number mappings

### 4. Adding Inline Comments

```bash
gh pr comment <PR_NUMBER> --repo <OWNER/REPO> --body "<COMMENT>"
```

For line-specific comments:
```bash
gh pr comment <PR_NUMBER> --repo <OWNER/REPO> \
  --body "<COMMENT>" \
  --body-file - <<EOF
Reviewing: <FILE_PATH>:<LINE_NUMBER>

<DETAILED_FEEDBACK>
EOF
```

### 5. Submitting a Review

```bash
# Approve
gh pr review <PR_NUMBER> --repo <OWNER/REPO> --approve --body "<REVIEW_SUMMARY>"

# Request changes
gh pr review <PR_NUMBER> --repo <OWNER/REPO> --request-changes --body "<FEEDBACK>"

# Comment only
gh pr review <PR_NUMBER> --repo <OWNER/REPO> --comment --body "<OBSERVATIONS>"
```

## Working with Large PRs

When a PR has 100+ files or 5000+ line changes:

### Strategy 1: File-by-File Review

```bash
# Get list of changed files
gh pr diff <PR_NUMBER> --name-only

# Review high-priority files first (I'll identify these)
# - Files with most changes
# - Core functionality files
# - Security-sensitive files
```

### Strategy 2: Directory-Based Review

```bash
# Review by directory
gh pr diff <PR_NUMBER> -- src/auth/
gh pr diff <PR_NUMBER> -- src/api/
gh pr diff <PR_NUMBER> -- tests/
```

### Strategy 3: Change Type Review

```bash
# New files
gh pr diff <PR_NUMBER> --diff-filter=A

# Modified files
gh pr diff <PR_NUMBER> --diff-filter=M

# Deleted files
gh pr diff <PR_NUMBER> --diff-filter=D
```

## Context Management

### Automatic Chunking

For large file diffs, I will:

1. **Parse the diff into hunks**: Each `@@ ... @@` block is a logical unit
2. **Estimate token count**: ~1 token per 3.5 characters for code
3. **Group hunks**: Keep related changes together (max 4000 tokens/chunk)
4. **Preserve overlap**: Include 3 lines of context between chunks
5. **Maintain line numbers**: Track original and modified line positions

### Manual Chunk Navigation

If you need specific sections:

```bash
# Show specific line ranges
gh pr diff <PR_NUMBER> -- <FILE> | sed -n '<START>,<END>p'
```

## Review Workflow

### Complete Review Process

1. **Initial Overview**
```bash
gh pr view <PR_NUMBER> --json title,body,additions,deletions,changedFiles
```

2. **File Categorization**
- Critical: Security, auth, payment logic
- High: Core features, API endpoints
- Medium: Utilities, helpers, refactoring
- Low: Tests, docs, configs

3. **Detailed Review**
- Read each file diff
- Check for code quality issues
- Verify tests cover changes
- Look for security vulnerabilities

4. **Feedback Compilation**
- Add inline comments for specific issues
- Note patterns across files
- Prepare summary with actionable items

5. **Review Submission**
- Choose appropriate review type (approve/request changes/comment)
- Include summary of findings
- Reference specific files and lines

## Common Patterns

### Pattern 1: Security Review

Focus on:
- Input validation
- Authentication checks
- SQL injection vulnerabilities
- XSS prevention
- Sensitive data handling

### Pattern 2: Performance Review

Look for:
- N+1 queries
- Inefficient loops
- Memory leaks
- Unnecessary re-renders
- Missing caching

### Pattern 3: Code Quality Review

Check for:
- Code duplication
- Complex functions (>50 lines)
- Missing error handling
- Unclear variable names
- Missing comments for complex logic

### Pattern 4: Test Coverage Review

Verify:
- New features have tests
- Edge cases covered
- Error paths tested
- Integration tests present

## Advanced Operations

### Working with Draft PRs

```bash
# View draft status
gh pr view <PR_NUMBER> --json isDraft

# Mark as ready for review
gh pr ready <PR_NUMBER>
```

### Checking CI Status

```bash
# View all checks
gh pr checks <PR_NUMBER>

# Watch checks in real-time
gh pr checks <PR_NUMBER> --watch
```

### Viewing PR Comments

```bash
# All comments
gh pr view <PR_NUMBER> --json comments --jq '.comments[].body'

# Review comments
gh pr view <PR_NUMBER> --json reviews --jq '.reviews[]'
```

### Managing Review Threads

```bash
# Add to existing thread
gh pr comment <PR_NUMBER> --body "Additional context: ..."
```

## Error Handling

### Common Issues

1. **PR Not Found**
```bash
# Verify PR exists
gh pr list --repo <OWNER/REPO> | grep <PR_NUMBER>
```

2. **Permission Denied**
```bash
# Check authentication
gh auth status

# Re-authenticate if needed
gh auth login --scopes repo
```

3. **Rate Limit Exceeded**
```bash
# Check rate limit
gh api rate_limit

# Wait for reset or use personal access token
```

4. **File Too Large**
```bash
# Use git directly for very large files
git show origin/pr/<PR_NUMBER>:<FILE_PATH>
```

## Best Practices

### 1. Start Broad, Then Focus
- Read PR description first
- Get file list overview
- Identify areas needing attention
- Deep dive into critical files

### 2. Provide Actionable Feedback
- Be specific about what needs to change
- Suggest concrete improvements
- Include code examples when helpful
- Link to relevant documentation

### 3. Use Inline Comments Wisely
- Comment on specific issues, not general observations
- Use PR-level comments for overall feedback
- Reference line numbers explicitly

### 4. Balance Thoroughness and Efficiency
- Don't nitpick minor style issues
- Focus on functionality, security, and maintainability
- Trust CI/CD for formatting and linting

### 5. Collaborate Effectively
- Ask questions if intent is unclear
- Acknowledge good implementations
- Suggest alternatives, don't demand them
- Be respectful and constructive

## Integration with Other Tools

### With Git

```bash
# Checkout PR locally for testing
gh pr checkout <PR_NUMBER>

# View PR in browser
gh pr view <PR_NUMBER> --web
```

### With Diff Tools

```bash
# Export diff to file
gh pr diff <PR_NUMBER> > pr_changes.diff

# Use with diff tool
diff-so-fancy < pr_changes.diff
```

### With Code Analysis

```bash
# Run linters on changed files
gh pr diff <PR_NUMBER> --name-only | xargs eslint

# Run tests on changed code
gh pr diff <PR_NUMBER> --name-only | xargs npm test
```

## Detailed References

For comprehensive information, see:
- [PR Operations Reference](PR-OPERATIONS.md) - Complete GitHub CLI command reference
- [Usage Examples](EXAMPLES.md) - Real-world PR review scenarios
- [Utility Scripts](scripts/) - Helper scripts for complex operations

## Troubleshooting

### Skill Not Working

1. Verify GitHub CLI installation:
```bash
gh --version
```

2. Check authentication:
```bash
gh auth status
```

3. Test basic PR access:
```bash
gh pr list --limit 1
```

### Performance Issues

For very large PRs:
- Review in multiple sessions
- Use directory-based approach
- Focus on changed logic, skip trivial changes
- Use git locally instead of API for huge files

### Diff Format Issues

If diffs are hard to read:
```bash
# Use unified format
gh pr diff <PR_NUMBER> --patch

# Adjust context lines
git diff -U10  # 10 lines of context
```

## Summary

This skill enables you to:
- ✅ Read and analyze any PR, regardless of size
- ✅ Navigate large changesets without context overflow
- ✅ Add precise, line-specific comments
- ✅ Perform comprehensive code reviews
- ✅ Submit structured feedback
- ✅ Integrate seamlessly with GitHub workflow

Simply ask me to review a PR, and I'll handle all the complexity of context management, navigation, and structured feedback.
