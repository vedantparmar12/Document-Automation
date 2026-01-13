# Quick Start Guide
## Using the Refactored Document Automation System

**Last Updated:** 2026-01-13

---

## 🚀 **Instant Usage**

### **1. Use the Refactored Generator**

```python
from src.generators.professional_doc_generator_refactored import (
    ProfessionalDocumentationGenerator
)
from src.schemas import CodeAnalysisResult

# Create generator
generator = ProfessionalDocumentationGenerator.create_default()

# Prepare analysis
analysis = CodeAnalysisResult(
    project_name="My Project",
    project_type="Web Application",
    description="A modern web application",
    languages=["Python", "JavaScript"],
    frameworks=["Django", "React"],
    key_features={},
    file_structure={},
    dependencies={}
)

# Generate documentation
result = generator.generate(analysis)

# Access the documentation
print(result.content)  # Markdown content
print(result.format)   # DocumentationFormat.MARKDOWN
print(result.metadata) # Generation metadata
```

### **2. Run Tests**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Run only new module tests
pytest tests/unit/generators/
```

### **3. Use GitHub PR Manager Skill**

```bash
# Install GitHub CLI (if not installed)
brew install gh  # macOS
# or: winget install GitHub.cli  # Windows

# Authenticate
gh auth login

# Use in Claude Code
claude
> Review PR #123 in myorg/myrepo
```

---

## 📁 **Key Files Reference**

### **Refactored Components**

```
src/generators/
├── base_generator.py                        # 6 interfaces + base class
├── professional_doc_generator_refactored.py # Main orchestrator (USE THIS)
├── core/
│   ├── content_generator.py                 # Content generation
│   ├── markdown_formatter.py                # Markdown formatting
│   ├── diagram_integrator.py                # Diagram integration
│   └── theme_manager.py                     # Theme management
└── exporters/
    ├── html_exporter.py                     # HTML export
    └── pdf_exporter.py                      # PDF export
```

### **Tests**

```
tests/unit/generators/
├── test_content_generator.py     # 8 tests
├── test_markdown_formatter.py    # 17 tests
└── test_refactored_generator.py  # 8 tests
```

### **Documentation**

- **REFACTORING_COMPLETE.md** - Complete summary of work done
- **REFACTORING_PLAN.md** - Original refactoring plan
- **tests/README.md** - Testing guide
- **.claude/skills/github-pr-manager/** - GitHub PR skill

---

## 🎯 **Common Tasks**

### **Generate Documentation (Basic)**

```python
generator = ProfessionalDocumentationGenerator.create_default()
result = generator.generate(analysis)
```

### **Generate Documentation (Custom Config)**

```python
config = {
    'format': 'html',
    'theme': 'dark',
    'include_diagrams': True,
    'include_toc': True,
    'output_path': 'docs/documentation.html'
}

result = generator.generate(analysis, config)
```

### **Use Custom Components (DI)**

```python
from src.generators.core import ContentGenerator, MarkdownFormatter

generator = ProfessionalDocumentationGenerator(
    content_generator=ContentGenerator(),
    formatter=MarkdownFormatter(),
    # Other dependencies...
)
```

### **Export to Different Formats**

```python
# Markdown (default)
result = generator.generate(analysis, {'format': 'markdown'})

# HTML
result = generator.generate(analysis, {
    'format': 'html',
    'output_path': 'docs/output.html'
})

# PDF
result = generator.generate(analysis, {
    'format': 'pdf',
    'output_path': 'docs/output.pdf'
})
```

---

## 🧪 **Testing**

### **Run All Tests**
```bash
pytest
```

### **Run Specific Module**
```bash
pytest tests/unit/generators/test_content_generator.py -v
```

### **Run with Coverage**
```bash
pytest --cov=src --cov-report=term-missing
```

### **Run Only Fast Tests**
```bash
pytest -m "not slow"
```

---

## 🔧 **Extending the System**

### **Add Custom Formatter**

```python
from src.generators.base_generator import IFormatter

class MyFormatter(IFormatter):
    def format_heading(self, text: str, level: int = 1) -> str:
        return f"{'#' * level} {text}\n"

    def format_paragraph(self, text: str) -> str:
        return f"{text}\n\n"

    # Implement other methods...
```

### **Add Custom Content Generator**

```python
from src.generators.base_generator import IContentGenerator

class MyContentGenerator(IContentGenerator):
    def generate_overview(self, analysis):
        return f"Custom overview for {analysis.project_name}"

    # Implement other methods...
```

### **Use Custom Components**

```python
generator = ProfessionalDocumentationGenerator(
    content_generator=MyContentGenerator(),
    formatter=MyFormatter()
)
```

---

## 📚 **Documentation**

| Document | Purpose |
|----------|---------|
| **REFACTORING_COMPLETE.md** | Complete summary of refactoring work |
| **REFACTORING_PLAN.md** | Original 4-week refactoring plan |
| **CLEANUP_SUMMARY.md** | Phase 1 cleanup results |
| **PROJECT_STATUS.md** | Current status and metrics |
| **tests/README.md** | Testing guide and best practices |

---

## ❓ **Troubleshooting**

### **Import Errors**

```bash
# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### **Test Failures**

```bash
# Check if all dependencies installed
pip list

# Re-run tests with verbose output
pytest -vv
```

### **Missing Modules**

```bash
# Ensure you're in the correct directory
cd "Document Automation"

# Verify Python path
python -c "import sys; print(sys.path)"
```

---

## 🎓 **Key Concepts**

### **Dependency Injection**
- All dependencies injected via constructor
- Easy to test (mock interfaces)
- Easy to extend (new implementations)

### **SOLID Principles**
- **S**ingle Responsibility: Each class does ONE thing
- **O**pen/Closed: Extend via new classes, not modifications
- **L**iskov Substitution: All implementations interchangeable
- **I**nterface Segregation: Small, focused interfaces
- **D**ependency Inversion: Depend on abstractions

### **Interfaces**
- `IContentGenerator` - Generate content sections
- `IFormatter` - Format content
- `IDiagramIntegrator` - Handle diagrams
- `IThemeManager` - Manage themes
- `IExporter` - Export to formats

---

## 📞 **Getting Help**

- **Architecture Questions:** See REFACTORING_PLAN.md
- **Usage Examples:** See code examples above
- **Testing Help:** See tests/README.md
- **GitHub PR Skill:** See .claude/skills/github-pr-manager/README.md

---

**Everything is documented and ready to use! 🚀**
