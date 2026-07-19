#!/usr/bin/env bash
set -e

# Resolve project directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VENV_DIR="$DIR/.venv"

# Create .venv if it does not exist
if [ ! -d "$VENV_DIR" ]; then
    echo "[mcp-speak] Creating virtual environment in $VENV_DIR..." >&2
    python3 -m venv "$VENV_DIR"
    echo "[mcp-speak] Installing dependencies from requirements.txt..." >&2
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip >&2
    "$VENV_DIR/bin/pip" install --quiet -r "$DIR/requirements.txt" >&2
    echo "[mcp-speak] Virtual environment successfully initialized." >&2
fi

# Execute server using the virtual environment python
exec "$VENV_DIR/bin/python" "$DIR/speak_server.py" "$@"
