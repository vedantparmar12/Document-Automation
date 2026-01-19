# Quick Start - Document Automation

Get started with Document Automation in 5 minutes.

## 1. Install

```bash
# Clone repository
git clone https://github.com/vedantparmar12/Document-Automation.git
cd Document-Automation

# Install dependencies
pip install -r requirements.txt
```

## 2. Verify Installation

```bash
# Run verification script
./scripts/verify-install.sh

# Or test manually
python -c "from src.analyzers.codebase_analyzer import CodebaseAnalyzer; print('OK')"
```

## 3. Analyze a Repository

### GitHub Repository
```
Analyze https://github.com/facebook/react
```

### Local Directory
```
Analyze my project at /path/to/project
```

## 4. Generate Documentation

```
Generate documentation for this project in Markdown format
```

## 5. Configure Claude Desktop (Optional)

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "document-automation": {
      "command": "python",
      "args": ["/path/to/Document-Automation/src/main.py"]
    }
  }
}
```

## Quick Commands

| Task | Command |
|------|---------|
| Analyze GitHub repo | `Analyze https://github.com/user/repo` |
| Analyze local project | `Analyze /path/to/project` |
| Generate README | `Generate README for this project` |
| Document APIs | `Document API endpoints` |
| Create HTML docs | `Generate HTML documentation` |

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `GITHUB_TOKEN` | Private repo access | `ghp_xxxx...` |

## Troubleshooting

**Import errors?**
```bash
cd Document-Automation
pip install -e .
```

**Rate limited?**
```bash
export GITHUB_TOKEN=ghp_your_token
```

**Large repo timeout?**
Use `--shallow` flag or reduce `--max-depth`.

## Next Steps

- Read [SKILL.md](SKILL.md) for full capabilities
- See [EXAMPLES.md](EXAMPLES.md) for real-world usage
- Check [MCP-TOOLS.md](MCP-TOOLS.md) for tool reference
