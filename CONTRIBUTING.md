# Contributing to Codex Python SDK

Thank you for your interest in contributing to the Codex Python SDK! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kelleyblackmore/codex-py.git
   cd codex-py
   ```

2. **Install dependencies**
   ```bash
   # Install the package in development mode
   pip install -e ".[dev]"
   ```

3. **Install the Codex CLI**
   
   The SDK requires the Codex CLI to be installed. Choose one of:
   ```bash
   # Via npm
   npm install -g @openai/codex
   
   # Via Homebrew (macOS)
   brew install --cask codex
   
   # Or download from GitHub Releases
   # https://github.com/openai/codex/releases
   ```

## Project Structure

```
codex-py/
├── codex_sdk/           # Main package code
│   ├── __init__.py     # Package exports
│   ├── codex.py        # Main Codex client
│   ├── thread.py       # Thread management
│   ├── exec.py         # CLI execution layer
│   ├── events.py       # Event type definitions
│   └── items.py        # Item type definitions
├── examples/           # Usage examples
├── tests/              # Test suite
├── pyproject.toml      # Package configuration
├── setup.py            # Setup script
└── README.md           # Main documentation
```

## Code Style

We follow PEP 8 and use the following tools:

- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

### Running Code Quality Tools

```bash
# Format code
black codex_sdk/ examples/

# Lint code
ruff check codex_sdk/ examples/

# Type check
mypy codex_sdk/
```

## Testing

We use pytest for testing:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=codex_sdk

# Run specific test file
pytest tests/test_codex.py
```

## Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, documented code
   - Add type hints to all functions
   - Follow existing code style

3. **Add tests**
   - Add tests for new features
   - Ensure existing tests still pass

4. **Update documentation**
   - Update README.md if needed
   - Add docstrings to new functions
   - Update examples if API changes

5. **Run quality checks**
   ```bash
   black codex_sdk/ examples/
   ruff check codex_sdk/ examples/
   mypy codex_sdk/
   pytest
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

7. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Guidelines

- **Title**: Use a clear, descriptive title
- **Description**: Explain what changes you made and why
- **Tests**: Include tests for new features
- **Documentation**: Update docs as needed
- **Code Quality**: Ensure all checks pass

## Code Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged

## Reporting Issues

When reporting issues, please include:

- Python version
- Codex CLI version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)

## Questions?

Feel free to:
- Open an issue for bugs or feature requests
- Start a discussion for questions
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License.

## Code of Conduct

Please be respectful and professional in all interactions. We aim to maintain a welcoming and inclusive community.
