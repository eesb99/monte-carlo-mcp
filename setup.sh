#!/bin/bash
# Setup script for monte-carlo-mcp plugin
# Automatically creates venv and installs dependencies

PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PLUGIN_DIR/venv"

echo "Setting up monte-carlo-mcp plugin..."

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Install dependencies
echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$PLUGIN_DIR/requirements.txt"

# Create data directories (Monte Carlo specific)
mkdir -p "$PLUGIN_DIR/data/input"
mkdir -p "$PLUGIN_DIR/data/cache"
mkdir -p "$PLUGIN_DIR/data/exports"

echo "Setup complete! All dependencies installed."
