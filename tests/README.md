# Tests Directory

Comprehensive test suite for the Document Automation MCP project.

## Structure

```
tests/
├── conftest.py              # Shared fixtures and pytest configuration
├── README.md                # This file
│
├── unit/                    # Unit tests (isolated, fast)
│   ├── test_schemas.py      # Schema and type tests
│   ├── test_validation.py   # Validation logic tests
│   ├── generators/          # Generator module tests
│   ├── analyzers/           # Analyzer module tests
│   ├── tools/               # MCP tool tests
│   └── pagination/          # Pagination logic tests
│
├── integration/             # Integration tests (component interaction)
│   ├── test_full_workflow.py    # End-to-end workflow tests
│   └── test_mcp_protocol.py     # MCP protocol tests
│
└── fixtures/                # Test data and fixtures
    ├── sample_projects/     # Sample project structures
    └── expected_outputs/    # Expected documentation outputs
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Unit Tests Only
```bash
pytest tests/unit/ -m unit
```

### Run Integration Tests Only
```bash
pytest tests/integration/ -m integration
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html to view coverage report
```

### Run Specific Test File
```bash
pytest tests/unit/test_schemas.py -v
```

### Run Specific Test Function
```bash
pytest tests/unit/test_schemas.py::TestCodeAnalysisResult::test_create_minimal_analysis -v
```

### Run Tests Matching Pattern
```bash
pytest -k "validation" -v
```

## Test Markers

Tests are marked with the following markers:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Integration tests (slower)
- `@pytest.mark.slow` - Tests that take significant time

### Run Only Fast Tests (Skip Slow)
```bash
pytest -m "not slow"
```

## Writing Tests

### Basic Test Structure

```python
import pytest

@pytest.mark.unit
class TestMyComponent:
    """Test MyComponent class."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        component = MyComponent()

        # Act
        result = component.do_something()

        # Assert
        assert result == expected_value

    def test_error_handling(self):
        """Test error handling."""
        component = MyComponent()

        with pytest.raises(ValueError):
            component.invalid_operation()
```

### Using Fixtures

```python
@pytest.mark.unit
def test_with_sample_project(sample_project):
    """Test using sample project fixture."""
    # sample_project is a Path object to temporary project
    assert (sample_project / "README.md").exists()
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
@pytest.mark.unit
async def test_async_operation():
    """Test async operation."""
    result = await my_async_function()
    assert result is not None
```

### Parametrized Tests

```python
@pytest.mark.unit
@pytest.mark.parametrize("input,expected", [
    ("markdown", DocumentationFormat.MARKDOWN),
    ("html", DocumentationFormat.HTML),
    ("pdf", DocumentationFormat.PDF),
])
def test_format_conversion(input, expected):
    """Test format conversion with multiple inputs."""
    result = convert_format(input)
    assert result == expected
```

## Fixtures

### Available Fixtures (see conftest.py)

- **`sample_project`** - Temporary project with realistic structure
- **`empty_project`** - Empty temporary directory
- **`mock_analysis_result`** - Mock CodeAnalysisResult for testing
- **`mock_documentation_config`** - Mock configuration dictionary

### Creating Custom Fixtures

Add fixtures to `conftest.py` or test files:

```python
import pytest

@pytest.fixture
def my_custom_fixture():
    """Provide custom test data."""
    data = setup_data()
    yield data
    cleanup_data(data)  # Teardown after test
```

## Best Practices

### 1. Test Naming
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<what_it_tests>`
- Use descriptive names that explain what is being tested

### 2. Test Organization
- Group related tests in classes
- One assertion concept per test
- Use `# Arrange`, `# Act`, `# Assert` comments for clarity

### 3. Test Independence
- Tests should not depend on each other
- Use fixtures for setup/teardown
- Clean up resources (files, connections) after tests

### 4. Mocking
```python
from unittest.mock import Mock, patch

@pytest.mark.unit
def test_with_mock(mocker):
    """Test using mocked dependency."""
    mock_analyzer = mocker.Mock()
    mock_analyzer.analyze.return_value = {"status": "success"}

    result = my_function(mock_analyzer)
    assert result["status"] == "success"
```

### 5. Testing Exceptions
```python
@pytest.mark.unit
def test_invalid_input():
    """Test that invalid input raises appropriate exception."""
    with pytest.raises(ValueError, match="Invalid input"):
        function_that_should_raise("invalid")
```

## Coverage Goals

Target coverage levels:
- **Critical paths**: 100% coverage
- **Core modules**: 90%+ coverage
- **Utilities**: 80%+ coverage
- **Overall project**: 80%+ coverage

### Checking Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=term-missing

# Generate HTML report
pytest --cov=src --cov-report=html

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=80
```

## Continuous Integration

Tests run automatically on:
- Every commit (via pre-commit hook)
- Pull requests (via GitHub Actions)
- Main branch merges

### CI Configuration

See `.github/workflows/test.yml` for CI setup.

## Troubleshooting

### Tests Failing Locally But Pass in CI
- Check Python version matches CI
- Ensure all dependencies installed: `pip install -e ".[dev]"`
- Check for environment-specific paths

### Import Errors
- Install package in development mode: `pip install -e .`
- Ensure src/ is in PYTHONPATH

### Slow Tests
- Use `@pytest.mark.slow` marker
- Skip slow tests: `pytest -m "not slow"`
- Profile tests: `pytest --durations=10`

### Flaky Tests
- Avoid time-dependent assertions
- Use deterministic test data
- Mock external dependencies

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure tests pass: `pytest`
3. Check coverage: `pytest --cov=src`
4. Run linting: `black tests/ && flake8 tests/`
5. Update this README if adding new patterns

---

**Last Updated:** 2026-01-13
**Test Framework:** pytest 7.0+
**Coverage Tool:** pytest-cov 4.1+
