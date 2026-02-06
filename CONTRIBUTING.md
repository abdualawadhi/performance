# Contributing to Low-Code Performance Scanner

Thank you for your interest in contributing to the Low-Code Performance Scanner! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Accept responsibility and apologize when mistakes happen

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a branch** for your feature or bug fix
4. **Make your changes** following our coding standards
5. **Run tests** to ensure everything works
6. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher (for frontend)
- Git
- Docker (optional, for containerized development)

### Python Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/lowcode-performance-scanner.git
cd lowcode-performance-scanner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Setup (Alternative)

```bash
# Start all services
docker-compose up -d

# Start development services
docker-compose --profile dev up -d
```

## How to Contribute

### Reporting Bugs

Before creating a bug report, please:

1. Check the existing issues to avoid duplicates
2. Use the latest version to see if the bug is already fixed
3. Collect information about the bug (steps to reproduce, expected vs actual behavior)

When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment details** (OS, Python version, browser)
- **Screenshots** if applicable
- **Error logs** or stack traces

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear title**
- **Provide detailed description** of the proposed feature
- **Explain why this enhancement would be useful**
- **List possible alternatives** you've considered

### Pull Requests

1. Update the README.md with details of changes if applicable
2. Update the documentation in `/docs` folder
3. Ensure all tests pass
4. Update CHANGELOG.md with your changes
5. Link any relevant issues in the PR description

## Coding Standards

### Python Code Style

We follow PEP 8 with some modifications:

- **Line length**: 100 characters maximum
- **Docstrings**: Google style docstrings
- **Type hints**: Required for all function signatures
- **Imports**: Sorted with isort (black profile)

```python
"""Module docstring.

This module provides functionality for...
"""

from typing import Dict, List, Optional

from external_package import something

from lowcode_scanner.models import DeviceType


def example_function(
    url: str,
    device_type: DeviceType,
    timeout: Optional[int] = None
) -> Dict[str, float]:
    """Short description of the function.
    
    Longer description explaining what the function does,
    when to use it, and any important notes.
    
    Args:
        url: The URL to process.
        device_type: The device type for the scan.
        timeout: Optional timeout in seconds.
        
    Returns:
        Dictionary containing performance metrics.
        
    Raises:
        ValueError: If URL is invalid.
        TimeoutError: If operation exceeds timeout.
    """
    # Implementation
    pass
```

### Code Formatting

We use `black` for code formatting:

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .
```

### Import Sorting

We use `isort` for import sorting:

```bash
# Sort imports
isort .

# Check import sorting
isort --check-only .
```

### Linting

We use `flake8` for linting:

```bash
# Run linter
flake8 lowcode_scanner backend --max-line-length=100 --extend-ignore=E203,W503
```

### Type Checking

We use `mypy` for type checking:

```bash
# Run type checker
mypy lowcode_scanner --ignore-missing-imports
```

### Frontend Code Style

For TypeScript/React code:

- Use functional components with hooks
- Follow the existing component structure
- Use TypeScript strict mode
- Run `npm run lint` before committing

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lowcode_scanner --cov-report=html

# Run specific test file
pytest tests/test_scanner.py

# Run integration tests only
pytest -m integration

# Run with verbose output
pytest -v
```

### Writing Tests

- Use `pytest` for all tests
- Name test files with `test_` prefix
- Name test functions with `test_` prefix
- Use fixtures from `conftest.py` for common setup
- Mock external API calls
- Test both success and error cases

```python
import pytest
from lowcode_scanner.core import LowCodePerformanceScanner


def test_scanner_initialization():
    """Test that scanner initializes correctly."""
    scanner = LowCodePerformanceScanner()
    assert scanner is not None


@pytest.mark.asyncio
async def test_scan_url():
    """Test URL scanning."""
    scanner = LowCodePerformanceScanner()
    result = await scanner.scan_url("https://example.com")
    assert result.performance_matrix is not None
```

## Documentation

### Docstrings

All public functions, classes, and modules should have docstrings following the Google style:

```python
def calculate_score(metrics: Dict[str, float]) -> float:
    """Calculate overall performance score.
    
    Takes a dictionary of metrics and calculates a weighted
    performance score based on Core Web Vitals.
    
    Args:
        metrics: Dictionary containing performance metrics.
            Expected keys: 'lcp', 'fid', 'cls', 'fcp', 'ttfb'
            
    Returns:
        Performance score between 0 and 100.
        
    Raises:
        ValueError: If required metrics are missing.
        
    Example:
        >>> metrics = {'lcp': 2.5, 'fid': 100, 'cls': 0.1}
        >>> score = calculate_score(metrics)
        >>> print(f"Score: {score}/100")
    """
```

### README Updates

When adding new features:

1. Update the feature list in README.md
2. Add usage examples if applicable
3. Update the quick start if the workflow changes

### Documentation Files

Place detailed documentation in the `/docs` folder:

- `API.md` - API endpoint documentation
- `USER_GUIDE.md` - User-facing documentation
- `ARCHITECTURE.md` - System architecture documentation
- `DEPLOYMENT.md` - Deployment instructions

## Commit Messages

We follow the Conventional Commits specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types:

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, missing semi colons, etc)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Performance improvement
- **test**: Adding or correcting tests
- **chore**: Changes to build process or auxiliary tools

Examples:

```
feat(scanner): add support for Mendix platform

fix(browser): resolve memory leak in screenshot handler

docs(api): update endpoint documentation for batch scans

test(core): add unit tests for PlatformDetector
```

## Pull Request Process

1. **Update documentation** for any changed functionality
2. **Add tests** for new code
3. **Ensure CI passes** - all checks must be green
4. **Update CHANGELOG.md** with your changes under the "Unreleased" section
5. **Request review** from maintainers
6. **Address review feedback**
7. **Squash commits** if requested
8. **Merge** will be done by maintainers

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts
- [ ] CI checks passing

## Release Process

1. **Update version** in:
   - `setup.py`
   - `lowcode_scanner/__init__.py`
   - `lowcode_scanner/__main__.py`
   - `backend/main.py`

2. **Update CHANGELOG.md** - move changes to a new version section

3. **Create a git tag**:
   ```bash
   git tag -a v1.0.3 -m "Release version 1.0.3"
   git push origin v1.0.3
   ```

4. **GitHub Actions** will automatically:
   - Run all tests
   - Build Docker images
   - Publish to PyPI (on tag push)

## Questions?

- **General questions**: Open a GitHub Discussion
- **Bug reports**: Open a GitHub Issue
- **Security issues**: Email security@lowcode-scanner.com directly

## Attribution

This contributing guide was adapted from the [Atom Contributing Guide](https://github.com/atom/atom/blob/master/CONTRIBUTING.md) and [Facebook's Draft Contributing Guide](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md).

---

Thank you for contributing to the Low-Code Performance Scanner! 🚀
