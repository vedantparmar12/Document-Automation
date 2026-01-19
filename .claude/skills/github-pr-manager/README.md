# GitHub PR Manager Skill

A comprehensive Claude Code skill for intelligent GitHub pull request management, code review, and collaboration.

## Overview

This skill enables Claude to:
- 🔍 Read and analyze pull requests of any size
- 🧩 Intelligently navigate large PRs with automatic chunking
- 💬 Add contextual comments to specific code lines
- ✅ Perform structured code reviews with approval/change requests
- 🎯 Manage context window limitations automatically
- 🤖 Provide consistent review quality and thoroughness

## Installation

### 1. Prerequisites

Install and authenticate GitHub CLI:

```bash
# Install GitHub CLI (if not already installed)
# macOS
brew install gh

# Windows
winget install --id GitHub.cli

# Linux
sudo apt install gh  # Debian/Ubuntu
sudo dnf install gh  # Fedora

# Authenticate
gh auth login
```

Verify authentication:
```bash
gh auth status
```

### 2. Install the Skill

For **project-level** installation (recommended for teams):

```bash
# This skill is already in your project at:
# .claude/skills/github-pr-manager/

# Team members who clone the repo automatically get the skill
```

For **personal** installation (available across all projects):

```bash
# Copy skill to personal skills directory
cp -r .claude/skills/github-pr-manager ~/.claude/skills/

# Or create symlink
ln -s "$(pwd)/.claude/skills/github-pr-manager" ~/.claude/skills/github-pr-manager
```

For **plugin** distribution (share across multiple repos):

```bash
# Create plugin structure
mkdir -p my-plugin/skills
cp -r .claude/skills/github-pr-manager my-plugin/skills/

# Distribute plugin via package manager or git
```

### 3. Verify Installation

Start Claude Code and check if skill is available:

```bash
claude
```

Then ask Claude:
```
> What skills are available?
```

You should see `github-pr-manager` listed with its description.

## Usage

### Quick Start

Simply ask Claude to review a PR:

```
> Review PR #123 in myorg/myrepo
```

Claude will automatically:
1. Fetch PR metadata and assess complexity
2. Categorize files by priority (critical, high, medium, etc.)
3. Review files systematically
4. Provide structured feedback
5. Submit review with appropriate status

### Common Use Cases

#### 1. Small PR Review

```
> Review PR #456
```

Claude performs a quick, thorough review of all changes.

#### 2. Large PR Navigation

```
> Review PR #789 - it's a big one
```

Claude automatically:
- Breaks down the PR into manageable chunks
- Reviews by priority (critical files first)
- Manages context to prevent overflow
- Provides progress updates

#### 3. Security-Focused Review

```
> Do a security review of PR #321
```

Claude focuses on:
- Authentication/authorization issues
- SQL injection vulnerabilities
- XSS prevention
- Sensitive data handling
- Dependency vulnerabilities

#### 4. Performance Review

```
> Check PR #654 for performance issues
```

Claude looks for:
- N+1 query problems
- Inefficient algorithms
- Memory leaks
- Missing caching opportunities
- Database indexing issues

#### 5. Test Coverage Review

```
> Check test coverage for PR #987
```

Claude verifies:
- New features have tests
- Edge cases are covered
- Error paths are tested
- Test quality and assertions

#### 6. Add Specific Comments

```
> Add a comment to PR #123 on line 45 of src/auth.js suggesting to use const instead of var
```

#### 7. Approve PR

```
> Approve PR #456 with message "LGTM! Great implementation."
```

#### 8. Request Changes

```
> Request changes on PR #789 - there are security issues in the auth flow
```

## Skill Structure

```
github-pr-manager/
├── SKILL.md              # Main skill definition with instructions
├── README.md             # This file - installation and usage guide
├── PR-OPERATIONS.md      # Complete GitHub CLI command reference
├── EXAMPLES.md           # Real-world usage examples and scenarios
└── scripts/              # Utility scripts for complex operations
    ├── chunk-diff.sh     # Chunk large diffs into manageable pieces
    ├── analyze-pr.py     # Analyze PR complexity and provide metrics
    ├── review-helper.sh  # Interactive review assistant
    └── comment-manager.sh # Manage PR comments programmatically
```

## Utility Scripts

### analyze-pr.py

Analyze PR complexity and get review recommendations:

```bash
python scripts/analyze-pr.py <PR_NUMBER> <REPO>

# Example
python scripts/analyze-pr.py 123 owner/repo
```

**Output:**
- Complexity score (0-100)
- File categorization (critical, high, medium, low, tests, docs, config)
- Estimated review time
- Recommended review strategy
- File-by-file breakdown
- Warnings and alerts

### chunk-diff.sh

Split large PR diffs into manageable chunks:

```bash
./scripts/chunk-diff.sh <PR_NUMBER> <REPO> [MAX_LINES_PER_CHUNK]

# Example: 200 lines per chunk
./scripts/chunk-diff.sh 123 owner/repo 200
```

**Output:**
- Individual chunk files for each changed file
- Info files with metadata
- Progress tracking

### review-helper.sh

Interactive PR review assistant:

```bash
./scripts/review-helper.sh <PR_NUMBER> <REPO>

# Example
./scripts/review-helper.sh 123 owner/repo
```

**Features:**
- View PR description and metadata
- List and categorize changed files
- View specific file diffs
- Check CI/CD status
- Add comments interactively
- Submit reviews (approve/request changes/comment)
- Open PR in browser

### comment-manager.sh

Programmatic comment management:

```bash
# List all comments
./scripts/comment-manager.sh list <PR_NUMBER> <REPO>

# Add general comment
./scripts/comment-manager.sh add <PR_NUMBER> <REPO> "Comment text"

# Add inline comment
./scripts/comment-manager.sh add-inline <PR_NUMBER> <REPO> <FILE> <LINE> "Comment text"

# Reply to comment
./scripts/comment-manager.sh reply <PR_NUMBER> <REPO> <COMMENT_ID> "Reply text"

# Edit comment
./scripts/comment-manager.sh edit <PR_NUMBER> <REPO> <COMMENT_ID> "New text"

# Delete comment
./scripts/comment-manager.sh delete <PR_NUMBER> <REPO> <COMMENT_ID>
```

## Advanced Configuration

### Tool Restrictions

The skill is configured with allowed tools:
- `Read` - Read files and documentation
- `Bash(gh:*)` - GitHub CLI commands only
- `Bash(git:*)` - Git commands only
- `Grep` - Search code
- `Glob` - Find files
- `Write` - Create temporary files
- `Edit` - Edit files if needed

This ensures the skill operates safely within defined boundaries.

### Context Management

The skill automatically manages context for large PRs:

**Default limits:**
- Max tokens per chunk: 4,000
- Overlap lines between chunks: 3
- Context preservation: Automatic

**Chunking strategy:**
1. Parse diff into hunks (logical units)
2. Estimate tokens per hunk
3. Group hunks into chunks (max 4,000 tokens)
4. Preserve 3 lines of overlap for continuity
5. Maintain line number mappings

### Customization

You can customize the skill by editing `.claude/skills/github-pr-manager/SKILL.md`:

1. **Modify review checklist** - Add/remove items from the review process
2. **Change tool restrictions** - Adjust `allowed-tools` in frontmatter
3. **Add custom patterns** - Include organization-specific review criteria
4. **Adjust chunking** - Modify context window thresholds

Example customization:

```yaml
---
name: github-pr-manager
description: [Your custom description with trigger keywords]
allowed-tools:
  - Read
  - Bash(gh:*)
  - Bash(git:*)
  - Grep
  - Glob
  - YourCustomTool  # Add custom tools
model: claude-sonnet-4-20250514  # Specify model
---
```

## Integration with CI/CD

### Pre-commit Hook

Automatically check PR reviewability:

```bash
#!/bin/bash
# .git/hooks/pre-push

# Analyze PR before pushing
python .claude/skills/github-pr-manager/scripts/analyze-pr.py $PR_NUMBER $REPO

# Check complexity
COMPLEXITY=$(python .claude/skills/github-pr-manager/scripts/analyze-pr.py $PR_NUMBER $REPO --json | jq '.complexity_score')

if [ $COMPLEXITY -gt 80 ]; then
  echo "Warning: PR complexity is very high ($COMPLEXITY). Consider breaking into smaller PRs."
  read -p "Continue? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi
```

### GitHub Actions

Automated PR analysis on creation:

```yaml
# .github/workflows/pr-analysis.yml
name: PR Analysis

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install GitHub CLI
        run: |
          type -p curl >/dev/null || sudo apt install curl -y
          curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
          sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
          echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
          sudo apt update
          sudo apt install gh -y

      - name: Analyze PR
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          python .claude/skills/github-pr-manager/scripts/analyze-pr.py ${{ github.event.pull_request.number }} ${{ github.repository }}

      - name: Comment on PR
        if: steps.analyze.outputs.complexity_score > 70
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '⚠️ This PR has high complexity. Consider requesting a phased review.'
            })
```

## Troubleshooting

### Skill Not Triggering

**Problem:** Claude doesn't use the skill automatically.

**Solutions:**
1. Check skill is installed: `ls .claude/skills/github-pr-manager/SKILL.md`
2. Verify SKILL.md has valid YAML frontmatter
3. Use trigger keywords in your request: "review PR", "check PR", "PR #123"
4. Manually invoke: "Use the github-pr-manager skill to review PR #123"

### GitHub Authentication Issues

**Problem:** `gh` commands fail with authentication errors.

**Solutions:**
```bash
# Re-authenticate
gh auth login

# Check authentication status
gh auth status

# Refresh token
gh auth refresh

# Use with specific scopes
gh auth login --scopes "repo,read:org"
```

### Rate Limiting

**Problem:** "API rate limit exceeded" errors.

**Solutions:**
1. Check rate limit status: `gh api rate_limit`
2. Wait for reset: `gh api rate_limit --jq '.rate.reset' | xargs -I {} date -d @{}`
3. Use personal access token with higher limits
4. Implement caching for frequently accessed PRs

### Large PR Performance

**Problem:** Very large PRs are slow or cause context overflow.

**Solutions:**
1. Use chunking scripts: `./scripts/chunk-diff.sh`
2. Review in multiple sessions
3. Focus on high-priority files first
4. Use directory-based review approach
5. Lower max tokens per chunk (edit SKILL.md)

### Script Permissions

**Problem:** Scripts not executable.

**Solution:**
```bash
chmod +x .claude/skills/github-pr-manager/scripts/*.sh
```

### Windows Compatibility

**Problem:** Bash scripts don't work on Windows.

**Solutions:**
1. Use Git Bash: https://gitforwindows.org/
2. Use WSL (Windows Subsystem for Linux)
3. Use Python scripts instead (cross-platform)
4. PowerShell equivalents (community contributions welcome)

## Best Practices

### 1. Review Strategy

- **Small PRs (<100 lines):** Quick single-pass review
- **Medium PRs (100-500 lines):** Category-based review
- **Large PRs (>500 lines):** Phased review across multiple sessions

### 2. Commenting Guidelines

- Be specific and reference line numbers
- Provide code examples for suggestions
- Ask questions for unclear intent
- Acknowledge good implementations
- Use inline comments for specific issues
- Use PR-level comments for general feedback

### 3. Review Focus Areas

**Critical:**
- Security vulnerabilities
- Data loss risks
- Performance regressions
- Breaking changes

**Important:**
- Code quality and maintainability
- Test coverage
- Error handling
- Documentation

**Nice to Have:**
- Code style consistency
- Minor optimizations
- Refactoring opportunities

### 4. Team Collaboration

- Assign reviewers based on expertise
- Use review checklists consistently
- Provide actionable feedback
- Respond to comments promptly
- Use draft PRs for early feedback
- Break large changes into smaller PRs

## FAQ

**Q: Can Claude automatically merge PRs?**
A: No, the skill is configured for read and review operations only. Merging requires explicit user action for safety.

**Q: Does this work with private repositories?**
A: Yes, as long as your GitHub CLI is authenticated with appropriate permissions (`repo` scope).

**Q: Can I use this with GitHub Enterprise?**
A: Yes, configure `gh` to point to your enterprise instance: `gh config set git_protocol https`

**Q: How accurate is the complexity analysis?**
A: The complexity score is an estimate based on file count, line changes, and file types. It's a guide, not an absolute measure.

**Q: Can I customize the review checklist?**
A: Yes, edit `.claude/skills/github-pr-manager/SKILL.md` to add custom review criteria.

**Q: Does this work with other Git platforms (GitLab, Bitbucket)?**
A: Currently GitHub-specific via `gh` CLI. Community contributions for other platforms welcome.

**Q: How do I update the skill?**
A: For project skills, `git pull` latest changes. For personal skills, copy updated files to `~/.claude/skills/`.

## Contributing

Contributions are welcome! Areas for improvement:

- **Multi-platform support:** GitLab, Bitbucket integration
- **Windows compatibility:** PowerShell script equivalents
- **Enhanced analysis:** ML-based complexity scoring
- **Custom integrations:** Jira, Slack, Microsoft Teams
- **More review patterns:** Framework-specific checklists
- **Performance optimizations:** Caching, parallel requests

Submit issues and pull requests to the main repository.

## License

MIT License - see LICENSE file for details.

## Support

- **Documentation:** [SKILL.md](SKILL.md), [PR-OPERATIONS.md](PR-OPERATIONS.md), [EXAMPLES.md](EXAMPLES.md)
- **GitHub Issues:** [Report bugs and request features](https://github.com/your-org/repo/issues)
- **Community:** [Discussions and Q&A](https://github.com/your-org/repo/discussions)

## Acknowledgments

Built with:
- [GitHub CLI](https://cli.github.com/) - Official GitHub command-line tool
- [Claude Code](https://code.claude.com/) - AI-powered development assistant
- [Anthropic Claude](https://www.anthropic.com/) - Advanced AI assistant

## Changelog

### Version 1.0.0 (2026-01-13)

Initial release:
- ✅ PR reading and analysis
- ✅ Smart navigation for large PRs
- ✅ Inline commenting support
- ✅ Structured code reviews
- ✅ Context management
- ✅ Utility scripts (analyze, chunk, review helper, comment manager)
- ✅ Comprehensive documentation
- ✅ Real-world examples
- ✅ Integration patterns

---

**Happy Reviewing! 🚀**
