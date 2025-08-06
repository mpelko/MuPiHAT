# Development Guide

This document describes how to set up the development environment for the MuPiHAT project.

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) - A fast Python package installer and resolver

## Installing uv

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Via pip
pip install uv
```

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/MuPiHAT.git
   cd MuPiHAT
   ```

2. **Create and activate a virtual environment:**
   ```bash
   make venv
   source .venv/bin/activate  # On Linux/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

3. **Install development dependencies:**
   ```bash
   make dev-install
   ```

## Available Make Commands

Run `make help` to see all available commands:

- `make install` - Install production dependencies
- `make dev-install` - Install development dependencies
- `make venv` - Create virtual environment with uv
- `make format` - Format code with ruff
- `make lint` - Run ruff linter
- `make check` - Run linter and formatter (dry run)
- `make fix` - Auto-fix linting issues
- `make clean` - Clean up cache files
- `make sync` - Sync dependencies with uv

## Code Style

This project uses [Ruff](https://github.com/astral-sh/ruff) for code formatting and linting:

- **Formatting**: Ruff formats code similar to Black
- **Linting**: Ruff provides fast linting with rules from Flake8, pycodestyle, and others
- **Line length**: 88 characters (Black compatible)
- **Quote style**: Double quotes for strings

### VS Code Integration

The project includes VS Code settings that automatically:
- Format code on save using Ruff
- Show linting errors inline
- Organize imports automatically
- Recommend relevant extensions

## Project Structure

```
MuPiHAT/
├── src/                    # Source code
│   ├── mupihat.py         # Main application
│   └── mupihat_bq25792.py # BQ25792 charger IC interface
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── pyproject.toml         # Project configuration and Ruff settings
├── Makefile              # Development commands
└── .vscode/              # VS Code settings
    ├── settings.json     # Editor configuration
    └── extensions.json   # Recommended extensions
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run the linter and formatter: `make fix`
5. Commit your changes: `git commit -am 'Add your feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Create a Pull Request

## Dependency Management

This project uses uv for fast dependency resolution and installation:

- **Production dependencies**: Listed in `requirements.txt`
- **Development dependencies**: Listed in `requirements-dev.txt`
- **Project metadata**: Defined in `pyproject.toml`

To add new dependencies:
1. Add them to the appropriate requirements file
2. Run `make sync` to install the new dependencies