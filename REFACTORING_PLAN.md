# Document Automation - Refactoring Plan

## Executive Summary

This document outlines the comprehensive refactoring plan for the Document Automation MCP project to achieve SOLID principles, proper OOP design, and maintainable code structure.

**Current State:**
- 49 Python files in src/, ~22,100 lines of code
- 30-36% duplicate code (~6,000-8,000 lines)
- 3 files >1,000 lines each (monolithic)
- 25+ SOLID principle violations
- Minimal test coverage

**Goal:**
- Clean, maintainable codebase following SOLID principles
- Proper OOP design with dependency injection
- 80%+ test coverage
- Clear module responsibilities
- <500 lines per module

---

## Completed Cleanup (Phase 1) ✓

### Files Removed
- ✅ All debug files (debug_imports.py, debug_imports_v2.py, diagnose_mcp.py, diagnose_simple.py)
- ✅ Temporary files (21 tmpclaude-*.cwd files, debug_output.txt)
- ✅ Unused server implementations (server_fastmcp.py, server_minimal.py, server_windows_fix.py)
- ✅ Unused processing modules (background_processor.py, concurrent_analyzer.py, entire src/processing/ directory)

### Issues Fixed
- ✅ Duplicate imports in documentation_generator.py (lines 13-15)

**Result:** Reduced codebase by ~3,000 lines and 13 files

---

## Phase 2: Critical Refactorings (PRIORITY)

### 2.1. Refactor `professional_doc_generator.py` (2,707 lines → 5 modules)

**Problem:** Massive God Object doing everything

**Target Structure:**
```
src/generators/
├── __init__.py
├── base_generator.py              # Abstract base (150 lines)
│   └── BaseDocumentationGenerator (ABC)
│       - abstract generate()
│       - abstract format()
│       - abstract export()
│
├── core/
│   ├── __init__.py
│   ├── content_generator.py       # Core documentation content (400 lines)
│   │   └── ContentGenerator
│   │       - generate_overview()
│   │       - generate_architecture_section()
│   │       - generate_code_analysis()
│   │       - generate_file_structure()
│   │
│   ├── markdown_formatter.py      # Markdown formatting (300 lines)
│   │   └── MarkdownFormatter
│   │       - format_heading()
│   │       - format_list()
│   │       - format_code_block()
│   │       - format_table()
│   │
│   ├── diagram_integrator.py      # Diagram integration (250 lines)
│   │   └── DiagramIntegrator
│   │       - generate_architecture_diagram()
│   │       - generate_database_diagram()
│   │       - generate_workflow_diagram()
│   │       - embed_diagram()
│   │
│   └── theme_manager.py           # Theme/styling (200 lines)
│       └── ThemeManager
│           - load_theme()
│           - apply_theme()
│           - get_css()
│           - get_template()
│
├── exporters/
│   ├── __init__.py
│   ├── html_exporter.py           # HTML export (300 lines)
│   │   └── HTMLExporter
│   │       - export_to_html()
│   │       - apply_template()
│   │       - add_styling()
│   │
│   ├── pdf_exporter.py            # PDF export (250 lines)
│   │   └── PDFExporter
│   │       - export_to_pdf()
│   │       - configure_pdf_options()
│   │
│   └── format_converter.py        # Format conversion (200 lines)
│       └── FormatConverter
│           - markdown_to_html()
│           - markdown_to_pdf()
│           - html_to_pdf()
│
└── professional_doc_generator.py  # Main coordinator (400 lines)
    └── ProfessionalDocumentationGenerator
        - __init__(content_generator, formatters, exporters)  # DI
        - generate()  # Orchestrates workflow
        - export()    # Delegates to exporters
```

**SOLID Compliance:**
- **SRP:** Each class has ONE reason to change
- **OCP:** New formats/themes via strategy pattern, no modification
- **LSP:** All exporters implement BaseExporter interface
- **ISP:** Small, focused interfaces (IContentGenerator, IFormatter, IExporter)
- **DIP:** Depends on abstractions (interfaces), not concrete classes

**Implementation Steps:**
1. Create base_generator.py with abstract base class
2. Extract ContentGenerator from existing code
3. Extract MarkdownFormatter
4. Extract DiagramIntegrator
5. Extract ThemeManager
6. Create exporter interfaces and implementations
7. Refactor ProfessionalDocumentationGenerator to use dependency injection
8. Update imports throughout codebase
9. Add comprehensive tests for each module

**Estimated Effort:** 2-3 days

---

### 2.2. Refactor `codebase_analyzer.py` (1,029 lines → 4 modules)

**Problem:** Analysis + Orchestration + Pagination mixed together

**Target Structure:**
```
src/analyzers/
├── __init__.py
├── base_analyzer.py (existing, refactored)
│
├── orchestration/
│   ├── __init__.py
│   ├── analyzer_orchestrator.py   # Main coordinator (300 lines)
│   │   └── AnalyzerOrchestrator
│   │       - __init__(analyzers: List[IAnalyzer])  # DI
│   │       - analyze_project()
│   │       - coordinate_analyzers()
│   │       - aggregate_results()
│   │
│   └── pagination_manager.py      # Pagination logic (250 lines)
│       └── PaginationManager
│           - paginate_analysis()
│           - chunk_results()
│           - manage_context()
│
├── code/
│   ├── __init__.py
│   ├── feature_analyzer.py        # Code feature analysis (300 lines)
│   │   └── CodeFeatureAnalyzer(IAnalyzer)
│   │       - analyze_features()
│   │       - detect_patterns()
│   │       - extract_classes()
│   │       - extract_functions()
│   │
│   └── dependency_analyzer.py     # Dependency analysis (250 lines)
│       └── DependencyAnalyzer(IAnalyzer)
│           - analyze_dependencies()
│           - build_dependency_graph()
│           - detect_circular_deps()
│
└── codebase_analyzer.py           # Simplified facade (200 lines)
    └── CodebaseAnalyzer
        - __init__(orchestrator, pagination_manager)  # DI
        - analyze()  # High-level interface
        - get_paginated_results()
```

**Key Improvements:**
- **Strategy Pattern:** Each analyzer is pluggable
- **Dependency Injection:** Analyzers injected into orchestrator
- **Single Responsibility:** Orchestration vs Analysis vs Pagination
- **Interface Segregation:** IAnalyzer interface for all analyzers

**Implementation Steps:**
1. Define IAnalyzer interface
2. Extract CodeFeatureAnalyzer
3. Extract DependencyAnalyzer
4. Create AnalyzerOrchestrator
5. Extract PaginationManager
6. Refactor CodebaseAnalyzer as facade
7. Update all imports
8. Add tests

**Estimated Effort:** 2 days

---

### 2.3. Refactor `consolidated_documentation_tools.py` (3 huge methods → tool classes)

**Problem:** 3 massive async methods (500+ lines each) in single class

**Target Structure:**
```
src/tools/
├── __init__.py
├── base_tool.py                   # Abstract tool base
│   └── BaseDocumentationTool(ABC)
│       - abstract execute()
│       - abstract validate_input()
│       - handle_errors()
│
├── handlers/
│   ├── __init__.py
│   ├── analysis_tool_handler.py   # Analysis operations (300 lines)
│   │   └── AnalysisToolHandler(BaseDocumentationTool)
│   │       - execute_analysis()
│   │       - validate_project_path()
│   │       - handle_analysis_errors()
│   │
│   ├── generation_tool_handler.py # Generation operations (350 lines)
│   │   └── GenerationToolHandler(BaseDocumentationTool)
│   │       - execute_generation()
│   │       - validate_format()
│   │       - handle_generation_errors()
│   │
│   └── export_tool_handler.py     # Export operations (250 lines)
│       └── ExportToolHandler(BaseDocumentationTool)
│           - execute_export()
│           - validate_export_params()
│           - handle_export_errors()
│
└── consolidated_documentation_tools.py  # MCP interface (200 lines)
    └── ConsolidatedDocumentationTools
        - __init__(analysis_handler, generation_handler, export_handler)  # DI
        - analyze_codebase() → delegates to analysis_handler
        - generate_documentation() → delegates to generation_handler
        - export_documentation() → delegates to export_handler
```

**Benefits:**
- Each handler can be tested independently
- Clear separation of concerns
- Easier to add new tools
- Better error handling per tool type

**Implementation Steps:**
1. Create BaseDocumentationTool abstract class
2. Extract AnalysisToolHandler
3. Extract GenerationToolHandler
4. Extract ExportToolHandler
5. Refactor ConsolidatedDocumentationTools to delegate
6. Add tests for each handler
7. Update server.py to use new structure

**Estimated Effort:** 1.5 days

---

## Phase 3: Generator Consolidation

### 3.1. Consolidate Multiple Generator Versions

**Current Problem:**
- `professional_doc_generator.py` imports `professional_doc_generator_v2.py` AND `beautiful_doc_generator.py`
- Conditional logic chooses between versions
- `documentation_generator.py` is legacy but still imported in server.py
- `interactive_doc_generator.py`, `mcp_doc_generator.py`, `readme_template.py` are unused

**Target:**
1. **Single unified generator** combining best features from all versions
2. **Strategy pattern** for different generation styles (professional, beautiful, interactive)
3. **Remove 5 files**, keep 1 main generator with pluggable strategies

**Implementation Steps:**
1. Analyze features unique to each generator version
2. Create GenerationStrategy interface
3. Implement ProfessionalStrategy, BeautifulStrategy
4. Refactor main generator to use strategy pattern
5. Migrate server.py to use unified generator
6. Remove old generator files
7. Update all imports
8. Add comprehensive tests

**Files to Remove After Migration:**
- documentation_generator.py
- professional_doc_generator_v2.py
- beautiful_doc_generator.py
- interactive_doc_generator.py
- mcp_doc_generator.py
- readme_template.py

**Estimated Effort:** 3 days

---

## Phase 4: Module Refactoring

### 4.1. Refactor `project_info_detector.py` (524 lines → 3 modules)

**Split into:**
```
src/analyzers/project/
├── metadata_extractor.py    # Project metadata (200 lines)
├── tree_builder.py           # Project tree structure (200 lines)
└── workflow_detector.py      # Workflow/pipeline detection (200 lines)
```

### 4.2. Clarify Pagination Module Responsibilities

**Current Structure (unclear):**
```
src/pagination/
├── chunker.py (628 lines)
├── strategies.py (657 lines)
├── context.py (445 lines)
└── token_estimator.py (335 lines)
```

**Refactor to:**
```
src/pagination/
├── __init__.py
├── interfaces.py              # IChunker, IStrategy, ITokenEstimator
├── chunker.py                 # Concrete chunker (400 lines, reduced)
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py       # Abstract strategy
│   ├── file_strategy.py       # File-based pagination
│   ├── token_strategy.py      # Token-based pagination
│   └── adaptive_strategy.py   # Adaptive pagination
├── context_manager.py         # Context management (300 lines)
└── token_estimator.py         # Token estimation (refactored, 250 lines)
```

### 4.3. Simplify Parser Structure

**Current Issue:** `ast_analyzer.py` duplicates `base_parser.py` functionality

**Action:**
- Merge `ast_analyzer.py` into `base_parser.py`
- Ensure all parsers properly implement abstract methods
- Add type hints to all parser methods

---

## Phase 5: Architecture Improvements

### 5.1. Implement Dependency Injection Throughout

**Create DI Container:**
```python
# src/di/container.py

from typing import Dict, Type, Any, Callable
import inspect

class DIContainer:
    """Simple dependency injection container"""

    def __init__(self):
        self._services: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}

    def register(self, interface: Type, implementation: Callable, singleton: bool = False):
        """Register a service"""
        self._services[interface] = implementation
        if singleton:
            self._singletons[interface] = None

    def resolve(self, interface: Type) -> Any:
        """Resolve a service instance"""
        # Check singleton cache
        if interface in self._singletons:
            if self._singletons[interface] is None:
                self._singletons[interface] = self._create_instance(interface)
            return self._singletons[interface]

        # Create new instance
        return self._create_instance(interface)

    def _create_instance(self, interface: Type) -> Any:
        """Create instance with dependency injection"""
        if interface not in self._services:
            raise ValueError(f"Service {interface} not registered")

        factory = self._services[interface]

        # Get constructor parameters
        sig = inspect.signature(factory)
        kwargs = {}

        for param_name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                # Recursively resolve dependencies
                kwargs[param_name] = self.resolve(param.annotation)

        return factory(**kwargs)

# Usage in server.py
def setup_di_container() -> DIContainer:
    """Configure dependency injection"""
    container = DIContainer()

    # Register services
    container.register(IContentGenerator, ContentGenerator, singleton=False)
    container.register(IMarkdownFormatter, MarkdownFormatter, singleton=True)
    container.register(IDiagramIntegrator, DiagramIntegrator, singleton=True)
    container.register(IThemeManager, ThemeManager, singleton=True)

    container.register(
        IProfessionalDocGenerator,
        lambda: ProfessionalDocumentationGenerator(
            content_generator=container.resolve(IContentGenerator),
            formatter=container.resolve(IMarkdownFormatter),
            diagram_integrator=container.resolve(IDiagramIntegrator),
            theme_manager=container.resolve(IThemeManager)
        ),
        singleton=False
    )

    return container
```

### 5.2. Add Comprehensive Type Hints

**Goals:**
- 100% type hint coverage on public APIs
- Use `mypy` for type checking
- Add runtime type validation with `pydantic` where appropriate

**Priority Files:**
1. All interface definitions
2. All public methods in refactored modules
3. Tool handlers
4. Main server.py

### 5.3. Create Clear Module Interfaces

**Define interfaces for all major components:**

```python
# src/interfaces.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from src.schemas import DocumentationResult, CodeAnalysisResult

class IAnalyzer(ABC):
    """Interface for all analyzers"""

    @abstractmethod
    def analyze(self, project_path: str) -> CodeAnalysisResult:
        """Analyze project and return results"""
        pass

class IGenerator(ABC):
    """Interface for documentation generators"""

    @abstractmethod
    def generate(self, analysis: CodeAnalysisResult, format: str) -> DocumentationResult:
        """Generate documentation from analysis"""
        pass

class IExporter(ABC):
    """Interface for documentation exporters"""

    @abstractmethod
    def export(self, documentation: DocumentationResult, output_path: str) -> bool:
        """Export documentation to file"""
        pass

class IPaginator(ABC):
    """Interface for pagination strategies"""

    @abstractmethod
    def paginate(self, content: str, max_tokens: int) -> List[str]:
        """Paginate content into chunks"""
        pass
```

---

## Phase 6: Testing & Quality

### 6.1. Add Comprehensive Test Suite

**Target Coverage:** 80%+

**Test Structure:**
```
tests/
├── unit/
│   ├── generators/
│   │   ├── test_content_generator.py
│   │   ├── test_markdown_formatter.py
│   │   ├── test_diagram_integrator.py
│   │   └── test_exporters.py
│   ├── analyzers/
│   │   ├── test_feature_analyzer.py
│   │   ├── test_dependency_analyzer.py
│   │   └── test_orchestrator.py
│   ├── tools/
│   │   ├── test_analysis_handler.py
│   │   ├── test_generation_handler.py
│   │   └── test_export_handler.py
│   └── pagination/
│       ├── test_chunker.py
│       ├── test_strategies.py
│       └── test_token_estimator.py
│
├── integration/
│   ├── test_full_workflow.py
│   ├── test_mcp_protocol.py
│   └── test_generator_pipeline.py
│
└── fixtures/
    ├── sample_projects/
    └── expected_outputs/
```

**Testing Tools:**
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mocking support

### 6.2. Add Linting & Formatting

**Tools:**
- `black` - Code formatting
- `isort` - Import sorting
- `flake8` - Linting
- `mypy` - Type checking
- `pylint` - Additional linting

**Configuration:**
```toml
# pyproject.toml

[tool.black]
line-length = 100
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pylint]
max-line-length = 100
disable = ["C0111", "C0103"]
```

---

## Phase 7: Documentation

### 7.1. Create Architecture Documentation

**Create `docs/ARCHITECTURE.md`:**
- System overview
- Module responsibilities
- Data flow diagrams
- Dependency graphs
- Design patterns used
- Extension points

### 7.2. Update README

- Clear project description
- Installation instructions
- Usage examples
- Architecture overview (link to ARCHITECTURE.md)
- Contributing guidelines
- API documentation

### 7.3. Add Inline Documentation

- Docstrings for all public classes and methods
- Type hints on all functions
- Module-level docstrings explaining purpose
- Examples in docstrings where helpful

---

## Implementation Timeline

### Week 1: Critical Refactorings
- **Days 1-3:** Refactor professional_doc_generator.py
- **Days 4-5:** Refactor codebase_analyzer.py
- **Days 6-7:** Refactor consolidated_documentation_tools.py

### Week 2: Generator Consolidation & Module Refactoring
- **Days 1-3:** Consolidate generator versions
- **Days 4-5:** Refactor project_info_detector.py and pagination
- **Days 6-7:** Simplify parser structure

### Week 3: Architecture & DI
- **Days 1-2:** Implement DI container
- **Days 3-4:** Add type hints throughout
- **Days 5-6:** Create clear module interfaces
- **Day 7:** Update all imports and fix circular dependencies

### Week 4: Testing & Quality
- **Days 1-3:** Add unit tests (target 80% coverage)
- **Day 4:** Add integration tests
- **Days 5-6:** Set up linting, formatting, type checking
- **Day 7:** Documentation updates

---

## Success Metrics

### Code Quality
- [ ] No files >500 lines
- [ ] 0 SOLID principle violations
- [ ] 0 circular dependencies
- [ ] 0 duplicate code blocks
- [ ] 100% type hints on public APIs

### Testing
- [ ] 80%+ unit test coverage
- [ ] 90%+ critical path coverage
- [ ] All integration tests passing
- [ ] 0 flake8/pylint warnings

### Documentation
- [ ] Architecture doc complete
- [ ] README updated
- [ ] All public APIs documented
- [ ] Contributing guide added

### Performance
- [ ] No performance regressions
- [ ] Memory usage acceptable for large projects
- [ ] Response times <2s for typical projects

---

## Risk Mitigation

### Breaking Changes
- **Risk:** Refactoring breaks existing functionality
- **Mitigation:**
  - Write tests before refactoring
  - Refactor in small, testable increments
  - Keep old code until new code is tested
  - Use feature flags for gradual rollout

### Import Circular Dependencies
- **Risk:** New structure creates circular imports
- **Mitigation:**
  - Draw dependency graph before refactoring
  - Use interfaces to break cycles
  - Implement dependency injection
  - Test imports separately

### Performance Degradation
- **Risk:** DI and abstraction add overhead
- **Mitigation:**
  - Benchmark before and after
  - Use singleton pattern for expensive objects
  - Profile hot paths
  - Optimize only where needed

---

## Next Steps

1. **Review this plan** with team/stakeholders
2. **Set up git branch** for refactoring work
3. **Begin with Phase 2.1** (professional_doc_generator.py)
4. **Commit frequently** with clear messages
5. **Test thoroughly** after each major change
6. **Document as you go** (don't save for end)

---

## Appendix: Before/After Comparison

### Before Refactoring
- 49 files, 22,100 lines
- 3 files >1,000 lines
- 25+ SOLID violations
- 0% test coverage
- No type hints
- Unclear module responsibilities

### After Refactoring (Target)
- ~60 files, 18,000 lines (duplicate code removed)
- 0 files >500 lines
- 0 SOLID violations
- 80% test coverage
- 100% type hints on public APIs
- Clear, documented architecture

---

**Last Updated:** 2026-01-13
**Status:** Phase 1 Complete, Phase 2 In Progress
