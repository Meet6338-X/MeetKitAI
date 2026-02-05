# CLI Tool Template

> Command-line application with rich interface and configuration.

## Quick Start

```bash
# Install
pip install -e .

# Run
{{PROJECT_NAME}} --help
{{PROJECT_NAME}} init
{{PROJECT_NAME}} run --config config.yaml
```

## Structure

```
cli-tool/
├── src/
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py        # Entry point
│   │   └── commands/      # Command modules
│   │       ├── __init__.py
│   │       ├── init.py
│   │       ├── run.py
│   │       └── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration
│   │   └── utils.py       # Utilities
│   └── __init__.py
├── tests/
│   ├── test_cli.py
│   └── test_core.py
├── pyproject.toml
├── setup.py
├── requirements.txt
└── README.md
```

## Features

- 🎨 Rich terminal UI
- ⚙️ YAML/TOML configuration
- 📝 Auto-generated help
- 🔄 Progress bars
- 🎯 Command groups
- 🧪 Test coverage
- 📦 Easy installation

## Usage

```bash
# Initialize a new project
{{PROJECT_NAME}} init my-project

# Show configuration
{{PROJECT_NAME}} config show

# Run with options
{{PROJECT_NAME}} run --verbose --output results/

# Interactive mode
{{PROJECT_NAME}} interactive
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Build
python -m build
```
