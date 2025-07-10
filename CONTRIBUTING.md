# Contributing to pynosaur

Welcome to the pynosaur community! This guide covers how to contribute to both the pget package manager and create new applications for the pynosaur organization.

## Table of Contents

- [Contributing to pget](#contributing-to-pget)
- [Creating New Apps](#creating-new-apps)
- [Development Setup](#development-setup)
- [Testing Guidelines](#testing-guidelines)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Contributing to pget

### Getting Started

1. **Fork the repository**
   ```bash
   git clone git@github.com:your-username/pget.git
   cd pget
   ```

2. **Set up development environment**
   ```bash
   ./setup_dev.sh
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Workflow

1. **Make your changes** following the [code style guidelines](#code-style)

2. **Run tests**
   ```bash
   # Run all tests
   bazel test //test:test_pget
   
   # Run with coverage
   bazel test //test:test_pget --test_output=all
   
   # Run specific test
   bazel test //test:test_pget --test_filter=TestPackageManager
   ```

3. **Build and test the binary**
   ```bash
   bazel build //app:pget_bin
   ./bazel-bin/app/pget --help
   ```

4. **Run the demo**
   ```bash
   ./demo.py
   ```

### Key Areas for Contribution

- **Core Package Manager**: `app/core/package_manager.py`
- **CLI Interface**: `app/main.py`
- **Utilities**: `app/utils/`
- **Tests**: `test/test_pget.py`
- **Documentation**: `doc/pget.yaml`

## Creating New Apps

The pynosaur organization hosts individual CLI applications that can be installed via pget. Each app follows a standardized structure.

### App Structure Template

```
app-name/
├── app/
│   ├── __init__.py
│   ├── BUILD.bazel
│   ├── main.py              # CLI entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── BUILD.bazel
│   │   └── main_logic.py    # Core functionality
│   └── utils/
│       ├── __init__.py
│       └── BUILD.bazel
├── test/
│   ├── __init__.py
│   ├── BUILD.bazel
│   └── test_app.py
├── doc/
│   └── app-name.yaml        # App documentation
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── test.yml
├── BUILD.bazel
├── MODULE.bazel
├── MODULE.bazel.lock
├── .bazelrc
├── requirements.lock
├── WORKSPACE
├── LICENSE
├── README.md
└── .gitignore
```

### Creating a New App

1. **Create the repository**
   ```bash
   # Create new repo on GitHub under pynosaur organization
   # Clone it locally
   git clone git@github.com:pynosaur/your-app-name.git
   cd your-app-name
   ```

2. **Initialize the structure**
   ```bash
   # Copy the template structure
   # You can use yday as a reference: https://github.com/pynosaur/yday
   ```

3. **Set up Bazel configuration**
   ```bash
   # Copy MODULE.bazel from yday and update app name
   # Copy .bazelrc from yday
   ```

4. **Create the core application**
   - Write your main logic in `app/core/main_logic.py`
   - Create CLI interface in `app/main.py`
   - Add tests in `test/test_app.py`

5. **Document your app**
   - Update `doc/app-name.yaml` with app documentation
   - Write a clear README.md
   - Add usage examples

### App Requirements

#### 1. CLI Interface
Your app must have a clear CLI interface:

```python
#!/usr/bin/env python3

from core.main_logic import your_main_function

def main():
    result = your_main_function()
    print(result)

if __name__ == "__main__":
    main()
```

#### 2. Core Logic
Separate business logic from CLI:

```python
#!/usr/bin/env python3

def your_main_function():
    """Main application logic"""
    # Your implementation here
    return result
```

#### 3. Testing
Include comprehensive tests:

```python
#!/usr/bin/env python3

import unittest
from core.main_logic import your_main_function

class TestYourApp(unittest.TestCase):
    def test_main_function(self):
        # Your test implementation
        pass

if __name__ == '__main__':
    unittest.main()
```

#### 4. Documentation
Create a YAML documentation file (`doc/app-name.yaml`):

```yaml
NAME: your-app-name
VERSION: 0.1.0
DESCRIPTION: Brief description of your app
SYNOPSIS: your-app-name [OPTIONS]
USAGE: |
  your-app-name                   # Basic usage

OPTIONS: None

EXAMPLES:
  - command: your-app-name
    description: Basic usage
    output: "expected output"

DESCRIPTION_DETAILED: |
  Detailed description of your application.

FUNCTIONS:
  your_main_function:
    description: Description of main function
    returns: "Return type and description"
    implementation: "Brief implementation details"

AUTHOR: "Your Name"
LICENSE: "CC0 1.0 Universal"
REPOSITORY: "https://github.com/pynosaur/your-app-name"
BUGS: "Report bugs to: https://github.com/pynosaur/your-app-name/issues"
```

#### 5. CI/CD
Set up GitHub Actions for testing:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"
    
    - name: Run tests
      run: |
        cd test
        python -m unittest test_app.py -v
```

### App Guidelines

1. **Keep it simple**: Focus on one specific task
2. **Follow Unix philosophy**: Do one thing well
3. **Be cross-platform**: Work on Linux and macOS
4. **Use pure Python**: Avoid external dependencies when possible
5. **Include tests**: Comprehensive test coverage
6. **Document everything**: Clear README and usage examples
7. **Use Bazel**: Consistent build system across all apps

### Publishing Your App

1. **Complete development**
   - All tests passing
   - Documentation complete
   - CI/CD working

2. **Create release**
   - Tag a version: `git tag v0.1.0`
   - Push tag: `git push origin v0.1.0`
   - Create GitHub release

3. **Update pget registry**
   - Your app will be available via `pget install your-app-name`

## Development Setup

### Prerequisites

- Python 3.8+
- Bazel 6.0+
- Git

### Environment Setup

```bash
# Clone the repository
git clone git@github.com:pynosaur/pget.git
cd pget

# Run setup script
./setup_dev.sh

# Verify installation
bazel test //test:test_pget
```

### IDE Configuration

#### VS Code
- Install Python extension
- Configure Bazel extension
- Set up linting with flake8/black

#### PyCharm
- Configure Bazel integration
- Set up Python interpreter
- Configure test runner

## Testing Guidelines

### Test Structure

```python
#!/usr/bin/env python3

import unittest
from pathlib import Path
import sys

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from core.main_logic import your_function

class TestYourApp(unittest.TestCase):
    def test_basic_functionality(self):
        """Test basic functionality"""
        result = your_function()
        self.assertIsNotNone(result)
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Your edge case tests
        pass

if __name__ == '__main__':
    unittest.main()
```

### Test Commands

```bash
# Run all tests
bazel test //test:test_app

# Run with coverage
bazel test //test:test_app --test_output=all

# Run specific test
bazel test //test:test_app --test_filter=TestYourApp

# Run with Python directly
cd test && python -m unittest test_app.py -v
```

### Test Coverage

- Aim for 90%+ coverage
- Test edge cases and error conditions
- Include integration tests
- Test CLI interface

## Code Style

### Python Style Guide

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for all functions
- Keep functions small and focused

### File Structure

```python
#!/usr/bin/env python3
"""
Module docstring
"""

import standard_library
import third_party
import local_imports

# Constants
CONSTANT_NAME = "value"

def function_name(param: str) -> str:
    """
    Function docstring
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
    """
    # Implementation
    return result

class ClassName:
    """Class docstring"""
    
    def method_name(self) -> None:
        """Method docstring"""
        pass

if __name__ == "__main__":
    main()
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Functions**: `snake_case()`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Variables**: `snake_case`

## Pull Request Process

### Before Submitting

1. **Run tests**
   ```bash
   bazel test //test:test_pget
   ```

2. **Check code style**
   ```bash
   # Install flake8 and black
   pip install flake8 black
   
   # Check style
   flake8 app/ test/
   black --check app/ test/
   ```

3. **Update documentation**
   - Update relevant doc files
   - Add changelog entry
   - Update README if needed

### PR Guidelines

1. **Clear title**: Describe the change concisely
2. **Detailed description**: Explain what and why
3. **Reference issues**: Link related issues
4. **Include tests**: Add tests for new features
5. **Update docs**: Keep documentation current

### Review Process

1. **Automated checks**: CI/CD must pass
2. **Code review**: At least one approval required
3. **Documentation**: Ensure docs are updated
4. **Testing**: Verify tests pass locally

## Release Process

### For pget

1. **Update version**
   - Update version in relevant files
   - Update CHANGELOG.md

2. **Create release**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **Create GitHub release**
   - Add release notes
   - Upload binaries if needed

### For Apps

1. **Version bump**
   - Update version in doc/app-name.yaml
   - Update README.md if needed

2. **Create release**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. **Update pget registry**
   - App becomes available via pget

## Getting Help

- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check README and doc/ files
- **Examples**: Look at existing apps like yday

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## License

By contributing to pynosaur projects, you agree that your contributions will be licensed under the same license as the project (typically CC0 1.0 Universal).

---

Thank you for contributing to pynosaur! 🦕
