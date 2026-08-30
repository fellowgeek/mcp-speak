#!/usr/bin/env bash
set -e

# Resolve project directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VENV_DIR="$DIR/.venv"

# Create .venv if it does not exist
if [ ! -d "$VENV_DIR" ]; then
    echo "[mcp-speak] Creating virtual environment in $VENV_DIR..." >&2
    # Prefer Python 3.12 for torch 2.8 compatibility; fall back to the default
    PYTHON_BIN="python3"
    if command -v python3.12 >/dev/null 2>&1; then
        PYTHON_BIN="$(command -v python3.12)"
    elif [ -x "$HOME/.pyenv/shims/python3.12" ]; then
        PYTHON_BIN="$HOME/.pyenv/shims/python3.12"
    elif [ -x "$HOME/.pyenv/versions/3.12.13/bin/python3.12" ]; then
        PYTHON_BIN="$HOME/.pyenv/versions/3.12.13/bin/python3.12"
    fi
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    echo "[mcp-speak] Installing dependencies from requirements.txt..." >&2
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip >&2
    "$VENV_DIR/bin/pip" install --quiet -r "$DIR/requirements.txt" >&2
    echo "[mcp-speak] Virtual environment successfully initialized." >&2
fi

# Execute server using the virtual environment python
exec "$VENV_DIR/bin/python" "$DIR/speak_server.py" "$@"
