#!/usr/bin/env bash
#
# Download reference audio (.wav) and transcript (.txt) files for personas
# from the remote voice repository into the voices directory.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_URL="${MCP_SPEAK_VOICES_URL:-https://dl.justshare.me/voices}"

# Known personas supported by default.
# When adding a new persona, add it here or place its definition in personas/<name>.md.
DEFAULT_PERSONAS=(
    "agent_smith"
    "existential_emo"
    "grizzled_cowboy"
    "head_chef"
    "nature_narrator"
    "neutral_mainframe"
    "not_quite_meeseeks"
    "over_eager_intern"
    "poet"
    "pun_master"
    "sarcastic_senior"
    "tech_priest"
)

show_help() {
    cat << 'EOF'
Usage: ./dl.sh [OPTIONS] [PERSONA ...]

Download persona reference voice files (.wav) and transcripts (.txt)
from the remote voice server into this directory.

Options:
  -f, --force    Re-download and overwrite existing local files
  -h, --help     Show this help message and exit

Examples:
  ./dl.sh                   Check and download all missing persona files
  ./dl.sh -f                Force re-download all persona files
  ./dl.sh agent_smith       Download files for agent_smith only
EOF
}

# Verify curl is available
if ! command -v curl >/dev/null 2>&1; then
    echo "Error: 'curl' is required to download voice files but was not found." >&2
    exit 1
fi

FORCE=false
TARGET_PERSONAS=()

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2
            show_help
            exit 1
            ;;
        *)
            TARGET_PERSONAS+=("$1")
            shift
            ;;
    esac
done

add_unique_persona() {
    local candidate="$1"
    [ -n "$candidate" ] || return 0
    if [ ${#TARGET_PERSONAS[@]} -gt 0 ]; then
        for existing in "${TARGET_PERSONAS[@]}"; do
            if [ "$existing" = "$candidate" ]; then
                return 0
            fi
        done
    fi
    TARGET_PERSONAS+=("$candidate")
}

# If no specific personas were passed via CLI, discover all available personas
if [ ${#TARGET_PERSONAS[@]} -eq 0 ]; then
    # 1. Discover from personas/*.md
    PERSONAS_DIR="${SCRIPT_DIR}/../personas"
    if [ -d "$PERSONAS_DIR" ]; then
        for md_file in "$PERSONAS_DIR"/*.md; do
            [ -e "$md_file" ] || continue
            persona_name="$(basename "$md_file" .md)"
            if [ "$persona_name" != "base_guidelines" ]; then
                add_unique_persona "$persona_name"
            fi
        done
    fi

    # 2. Discover from speak_server.py voice designs
    SERVER_PY="${SCRIPT_DIR}/../speak_server.py"
    if [ -f "$SERVER_PY" ]; then
        server_keys="$(grep -E '^[[:space:]]*"[a-zA-Z0-9_]+":[[:space:]]*\{' "$SERVER_PY" 2>/dev/null | sed -E 's/^[[:space:]]*"([^"]+)":.*/\1/' || true)"
        for k in $server_keys; do
            if [ "$k" != "voice_designs" ]; then
                add_unique_persona "$k"
            fi
        done
    fi

    # 3. Ensure all default personas are included
    for def in "${DEFAULT_PERSONAS[@]}"; do
        add_unique_persona "$def"
    done
fi

echo "============================================================"
echo " MCP Speak - Persona Voice Downloader"
echo " Target directory: ${SCRIPT_DIR}"
echo " Source repository: ${BASE_URL}"
echo "============================================================"
echo ""

count_downloaded=0
count_skipped=0
count_not_found=0

for persona in "${TARGET_PERSONAS[@]}"; do
    echo "Persona: ${persona}"

    for ext in "wav" "txt"; do
        filename="${persona}.${ext}"
        dest_path="${SCRIPT_DIR}/${filename}"
        url="${BASE_URL}/${filename}"

        if [ -f "$dest_path" ] && [ "$FORCE" = "false" ]; then
            echo "  [EXISTS]    ${filename} (already present locally)"
            count_skipped=$((count_skipped + 1))
            continue
        fi

        temp_path="${dest_path}.tmp"
        # Attempt download; remote returns 418 / 404 if file is not hosted
        if curl -f -s -L --connect-timeout 10 -o "$temp_path" "$url"; then
            mv -f "$temp_path" "$dest_path"
            echo "  [DOWNLOAD]  ${filename} (successfully downloaded)"
            count_downloaded=$((count_downloaded + 1))
        else
            rm -f "$temp_path"
            echo "  [--]        ${filename} (not available on remote server)"
            count_not_found=$((count_not_found + 1))
        fi
    done

    echo ""
done

echo "============================================================"
echo " Summary:"
echo "   Downloaded:      ${count_downloaded}"
echo "   Already present: ${count_skipped}"
echo "   Remote missing:  ${count_not_found}"
echo "============================================================"
