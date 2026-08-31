#!/usr/bin/env sh
set -e

# Resolve project directory in a POSIX-compliant way
DIR="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"
VENV_DIR="$DIR/.venv"

# Check if a candidate Python binary is valid (executable, >= 3.10 and < 3.15, has venv)
is_valid_python() {
    candidate="$1"
    [ -n "$candidate" ] || return 1
    if [ -x "$candidate" ] || command -v "$candidate" >/dev/null 2>&1; then
        "$candidate" -c "import sys; assert (3, 10) <= sys.version_info < (3, 15); import venv" >/dev/null 2>&1
        return $?
    fi
    return 1
}

# Find the best available Python interpreter on macOS or Linux
find_python() {
    # 1. Check if uv is available and can locate a compatible Python interpreter
    if command -v uv >/dev/null 2>&1; then
        for ver in 3.12 3.11 3.13 3.10 ">=3.10,<3.15"; do
            uv_py="$(uv python find "$ver" 2>/dev/null || true)"
            if [ -n "$uv_py" ] && is_valid_python "$uv_py"; then
                echo "$uv_py"
                return 0
            fi
        done
    fi

    # 2. Check pyenv active versions (via pyenv which)
    if command -v pyenv >/dev/null 2>&1; then
        for cmd in python3.12 python3.11 python3.13 python3.10 python3; do
            pyenv_py="$(pyenv which "$cmd" 2>/dev/null || true)"
            if [ -n "$pyenv_py" ] && is_valid_python "$pyenv_py"; then
                echo "$pyenv_py"
                return 0
            fi
        done
    fi

    # 3. Check installed pyenv versions directly (even if not active in pyenv global)
    pyenv_root="${PYENV_ROOT:-$HOME/.pyenv}"
    if [ -d "$pyenv_root/versions" ]; then
        for ver_dir in "$pyenv_root/versions"/*; do
            if [ -d "$ver_dir" ]; then
                for candidate in "$ver_dir/bin/python3.12" "$ver_dir/bin/python3.11" "$ver_dir/bin/python3.13" "$ver_dir/bin/python3.10" "$ver_dir/bin/python3"; do
                    if is_valid_python "$candidate"; then
                        echo "$candidate"
                        return 0
                    fi
                done
            fi
        done
    fi

    # 4. Check Homebrew / standard system prefixes
    for bp in "/opt/homebrew" "/usr/local"; do
        for opt_ver in "python@3.12" "python@3.11" "python@3.13" "python@3.10"; do
            if is_valid_python "$bp/opt/$opt_ver/bin/python3"; then
                echo "$bp/opt/$opt_ver/bin/python3"
                return 0
            fi
        done
        for bin_name in "python3.12" "python3.11" "python3.13" "python3.10" "python3"; do
            if is_valid_python "$bp/bin/$bin_name"; then
                echo "$bp/bin/$bin_name"
                return 0
            fi
        done
    done

    # 5. Check macOS Frameworks (official python.org installations)
    for fw_ver in "3.12" "3.11" "3.13" "3.10" "Current"; do
        fw_bin="/Library/Frameworks/Python.framework/Versions/$fw_ver/bin/python3"
        if is_valid_python "$fw_bin"; then
            echo "$fw_bin"
            return 0
        fi
    done

    # 6. Check Conda / Miniforge / Anaconda
    for c_py in "$CONDA_PREFIX/bin/python3" "$HOME/miniforge3/bin/python3" "$HOME/miniconda3/bin/python3" "$HOME/anaconda3/bin/python3" "$HOME/mambaforge/bin/python3"; do
        if is_valid_python "$c_py"; then
            echo "$c_py"
            return 0
        fi
    done

    # 7. Check standard PATH executables (only after functional verification)
    for cmd in python3.12 python3.11 python3.13 python3.10 python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            path_py="$(command -v "$cmd")"
            if is_valid_python "$path_py"; then
                echo "$path_py"
                return 0
            fi
        fi
    done

    return 1
}

# Verify existing .venv integrity
if [ -d "$VENV_DIR" ]; then
    if ! "$VENV_DIR/bin/python" -c "import sys; assert (3, 10) <= sys.version_info < (3, 15); import mcp, soundfile" >/dev/null 2>&1; then
        echo "[mcp-speak] Existing virtual environment in $VENV_DIR is missing dependencies or broken. Rebuilding..." >&2
        rm -rf "$VENV_DIR"
    fi
fi

# Create .venv if it does not exist
if [ ! -d "$VENV_DIR" ]; then
    PYTHON_BIN="$(find_python || true)"
    if [ -z "$PYTHON_BIN" ]; then
        echo "[mcp-speak] Error: No compatible Python interpreter (>= 3.10, < 3.15) found on this system." >&2
        echo "[mcp-speak] Please install Python 3.12 using Homebrew:" >&2
        echo "[mcp-speak]     brew install python@3.12" >&2
        echo "[mcp-speak] Or install via pyenv:" >&2
        echo "[mcp-speak]     pyenv install 3.12.12 && pyenv global 3.12.12" >&2
        exit 1
    fi

    PY_VER="$("$PYTHON_BIN" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")"
    echo "[mcp-speak] Creating virtual environment using Python $PY_VER ($PYTHON_BIN)..." >&2

    if command -v uv >/dev/null 2>&1; then
        uv venv "$VENV_DIR" --python "$PYTHON_BIN" >&2
        echo "[mcp-speak] Installing dependencies from requirements.txt with uv..." >&2
        uv pip install --python "$VENV_DIR/bin/python" -r "$DIR/requirements.txt" >&2
    else
        "$PYTHON_BIN" -m venv "$VENV_DIR"
        echo "[mcp-speak] Installing dependencies from requirements.txt..." >&2
        "$VENV_DIR/bin/pip" install --quiet --upgrade pip >&2
        "$VENV_DIR/bin/pip" install --quiet -r "$DIR/requirements.txt" >&2
    fi
    echo "[mcp-speak] Virtual environment successfully initialized." >&2
fi

# Execute server using the virtual environment python
exec "$VENV_DIR/bin/python" "$DIR/speak_server.py" "$@"
