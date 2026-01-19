# Quick Start Guide - GitHub PR Manager Skill

Get started with the GitHub PR Manager skill in 5 minutes!

## Step 1: Install GitHub CLI (if not already installed)

### Windows
```powershell
winget install --id GitHub.cli
```

### macOS
```bash
brew install gh
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install gh
```

### Linux (Fedora/CentOS)
```bash
sudo dnf install gh
```

## Step 2: Authenticate with GitHub

```bash
gh auth login
```

Follow the prompts to:
1. Choose "GitHub.com" (or your enterprise instance)
2. Choose "HTTPS" as preferred protocol
3. Authenticate with web browser or paste token
4. Select scopes (choose "all" for full functionality)

Verify authentication:
```bash
gh auth status
```

You should see: "✓ Logged in to github.com as YOUR_USERNAME"

## Step 3: Verify Skill Installation

The skill is already installed in your project at:
```
.claude/skills/github-pr-manager/
```

Check the skill files:
```bash
ls .claude/skills/github-pr-manager/
```

You should see:
- SKILL.md (main skill definition)
- README.md (full documentation)
- PR-OPERATIONS.md (command reference)
- EXAMPLES.md (usage examples)
- scripts/ (utility scripts)

## Step 4: Test the Skill

Start Claude Code:
```bash
claude
```

Ask Claude to list available skills:
```
> What skills do I have?
```

You should see `github-pr-manager` in the list.

## Step 5: Use the Skill

### Example 1: Review a Small PR

```
> Review PR #123 in myorg/myrepo
```

Claude will:
1. Fetch the PR information
2. Analyze the changes
3. Review each file
4. Provide structured feedback
5. Ask if you want to approve or request changes

### Example 2: Analyze a Large PR

```
> Analyze the complexity of PR #456 in myorg/myrepo
```

Claude will:
1. Run the analysis script
2. Show complexity score
3. Categorize files by priority
4. Estimate review time
5. Recommend review strategy

### Example 3: Security Review

```
> Do a security review of PR #789 in myorg/myrepo
```

Claude will focus on:
- Authentication/authorization
- SQL injection risks
- XSS vulnerabilities
- Sensitive data handling
- Dependency security

### Example 4: Add a Comment

```
> Add a comment to PR #123 suggesting to add error handling at line 45 in src/api.js
```

Claude will:
1. Locate the file and line
2. Add an inline comment with your suggestion
3. Confirm the comment was added

## Common Commands

### List PRs in a Repository
```
> List all open PRs in myorg/myrepo
```

### Check PR Status
```
> What's the status of PR #123?
```

### View Changed Files
```
> Show me all files changed in PR #456
```

### Approve a PR
```
> Approve PR #789 with message "LGTM, great work!"
```

### Request Changes
```
> Request changes on PR #321 - missing test coverage
```

## Pro Tips

### 1. Use Repository Default
Set a default repository to avoid typing it every time:

```bash
# In your project directory
gh repo set-default owner/repo
```

Then you can just say:
```
> Review PR #123
```

### 2. Review Strategy for Large PRs

For PRs with 50+ files or 1000+ lines:

```
> Review PR #567 step by step, starting with critical files
```

Claude will:
1. Categorize files (critical, high, medium, low)
2. Review critical files first
3. Pause and summarize after each category
4. Let you decide whether to continue

### 3. Use Utility Scripts Directly

For complex analysis:

```bash
# Analyze PR complexity
python .claude/skills/github-pr-manager/scripts/analyze-pr.py 123 owner/repo

# Interactive review session
./.claude/skills/github-pr-manager/scripts/review-helper.sh 123 owner/repo

# Chunk large diffs
./.claude/skills/github-pr-manager/scripts/chunk-diff.sh 123 owner/repo 200
```

### 4. Focus Your Review

Be specific about what you want:

```
> Review PR #123 focusing on performance issues
> Review PR #456 for security vulnerabilities only
> Check test coverage for PR #789
> Review the authentication changes in PR #321
```

### 5. Batch Reviews

Review multiple PRs efficiently:

```
> Show me all open PRs in myorg/myrepo
> Review PRs #123, #124, and #125
```

## Troubleshooting

### Skill Not Activating

If Claude doesn't use the skill automatically:

1. **Verify installation:**
   ```bash
   cat .claude/skills/github-pr-manager/SKILL.md
   ```

2. **Use explicit invocation:**
   ```
   > Use the github-pr-manager skill to review PR #123
   ```

3. **Check trigger keywords:** Use "review PR", "check PR", "analyze PR"

### Authentication Issues

If `gh` commands fail:

```bash
# Re-authenticate
gh auth login

# Check status
gh auth status

# Refresh token
gh auth refresh
```

### Rate Limiting

If you hit GitHub API rate limits:

```bash
# Check rate limit status
gh api rate_limit

# See when it resets
gh api rate_limit --jq '.rate.reset' | date -d @{}
```

Wait for the reset time or authenticate with a personal access token for higher limits.

### Permission Errors

If you can't access a PR:

1. Verify you have access to the repository
2. For private repos, ensure token has `repo` scope
3. Re-authenticate with proper scopes:
   ```bash
   gh auth login --scopes "repo,read:org,write:discussion"
   ```

## Next Steps

### Learn More

- Read [README.md](README.md) for comprehensive documentation
- Check [EXAMPLES.md](EXAMPLES.md) for real-world scenarios
- Browse [PR-OPERATIONS.md](PR-OPERATIONS.md) for command reference

### Customize the Skill

Edit `.claude/skills/github-pr-manager/SKILL.md` to:
- Add organization-specific review criteria
- Modify review checklists
- Adjust tool permissions
- Change context window limits

### Share with Team

Commit the skill to version control:

```bash
git add .claude/skills/github-pr-manager/
git commit -m "Add GitHub PR Manager skill"
git push
```

Team members who clone the repo automatically get the skill!

### Integrate with CI/CD

See README.md for:
- GitHub Actions integration
- Pre-commit hooks
- Automated PR analysis
- Custom workflows

## Support

- **Documentation:** Full docs in [README.md](README.md)
- **Examples:** Real-world usage in [EXAMPLES.md](EXAMPLES.md)
- **Commands:** Complete reference in [PR-OPERATIONS.md](PR-OPERATIONS.md)
- **Issues:** Report problems or request features via GitHub Issues

## Success Checklist

- [ ] GitHub CLI installed and authenticated
- [ ] Skill files present in `.claude/skills/github-pr-manager/`
- [ ] Claude Code can see the skill
- [ ] Successfully reviewed a test PR
- [ ] Utility scripts are executable
- [ ] Team members have access (if sharing)

---

**You're all set! Start reviewing PRs with AI assistance! 🚀**
