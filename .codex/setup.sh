#!/bin/bash
set -e

# Determine repository root
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Create Python virtual environment
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# Upgrade pip and install project in development mode with dev extras
pip install --upgrade pip
pip install -e ".[dev]"

echo "Environment setup complete. Activate with 'source .venv/bin/activate'."
