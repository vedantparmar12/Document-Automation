"""
Pytest configuration and shared fixtures for Document Automation tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator

# Sample project structure for testing
SAMPLE_PROJECT_FILES = {
    "README.md": "# Sample Project\nThis is a test project.",
    "src/__init__.py": "",
    "src/main.py": """
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
""",
    "src/utils.py": """
def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b
""",
    "tests/__init__.py": "",
    "tests/test_main.py": """
from src.main import main

def test_main():
    assert True
""",
    ".gitignore": """
__pycache__/
*.pyc
.venv/
""",
    "requirements.txt": """
pytest>=7.0.0
black>=22.0.0
""",
}


@pytest.fixture
def sample_project() -> Generator[Path, None, None]:
    """
    Create a temporary sample project structure for testing.

    Yields:
        Path: Path to the temporary project directory
    """
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create all files
        for file_path, content in SAMPLE_PROJECT_FILES.items():
            full_path = temp_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')

        yield temp_dir

    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


@pytest.fixture
def empty_project() -> Generator[Path, None, None]:
    """
    Create an empty temporary project directory.

    Yields:
        Path: Path to the empty temporary directory
    """
    temp_dir = Path(tempfile.mkdtemp())

    try:
        yield temp_dir
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


@pytest.fixture
def mock_analysis_result():
    """
    Provide a mock CodeAnalysisResult for testing generators.

    Returns:
        dict: Mock analysis result data
    """
    return {
        "project_name": "TestProject",
        "project_type": "Python Library",
        "description": "A test project for unit testing",
        "languages": ["Python"],
        "frameworks": ["pytest"],
        "key_features": {
            "functions": ["main", "add", "multiply"],
            "classes": [],
            "tests": ["test_main"],
        },
        "file_structure": {
            "src/": ["main.py", "utils.py", "__init__.py"],
            "tests/": ["test_main.py", "__init__.py"],
        },
        "dependencies": {
            "pytest": ">=7.0.0",
            "black": ">=22.0.0",
        },
        "database_info": None,
        "api_endpoints": [],
        "security_features": [],
    }


@pytest.fixture
def mock_documentation_config():
    """
    Provide a mock documentation configuration.

    Returns:
        dict: Mock configuration data
    """
    return {
        "format": "markdown",
        "include_diagrams": True,
        "include_metrics": True,
        "theme": "default",
        "output_directory": None,
    }


# Mark all tests as async by default for MCP testing
@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
