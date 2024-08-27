# NOVA Python Client

## Getting Started

### Prerequisites

- Python (>= 3.12)

### Installation

```bash
# Create a virtual environment
virtualenv -p python3.12 venv

# Activate the virtual environment
source venv/bin/activate

# Install package (editable)
pip install -e '.[dev]'

# Install pre-commit hooks
pre-commit install
```

### Running tests

Create a `.env` file with api key and bot id

```
NOVA_API_KEY="..."
BOT_ID="bot-..."
```

### Build & Publish

Please update the version in the `__init__.py` file.

Build

```
python3 -m build
```

Publish

```
python3 -m pip install --upgrade twine
python3 -m twine upload --repository pypi dist/*
```

### Use it locally for testing

```
python -m pip install -e /path/to/nova-python-client/
```
