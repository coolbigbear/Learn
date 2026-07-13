#!/usr/bin/env bash
# =============================================================================
# Build Sandbox Runner Images
#
# Usage:
#   ./build.sh              # Build ALL known images
#   ./build.sh python       # Build only the Python image
#   ./build.sh python node  # Build Python and Node images
#
# Images are tagged as tutorial-runner-<lang>:latest and used by the
# DockerRunner service at runtime.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY_DIR="$(dirname "$SCRIPT_DIR")/images"

# ── Image definitions ───────────────────────────────────────────────────────
# (lang)  (dockerfile_path)           (image_tag)
IMAGES=(
  "python:${SCRIPT_DIR}/Dockerfile.python:tutorial-runner-python:latest"
)

# ── Colors ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

build_image() {
    local lang="$1"
    local dockerfile="$2"
    local tag="$3"

    echo -e "${GREEN}━━━ Building ${tag} (${lang}) ─━━${NC}"
    echo "  Dockerfile: ${dockerfile}"

    if [ ! -f "$dockerfile" ]; then
        echo -e "${RED}ERROR: Dockerfile not found: ${dockerfile}${NC}"
        return 1
    fi

    docker build \
        --file "$dockerfile" \
        --tag "$tag" \
        --rm \
        "$SCRIPT_DIR"

    echo -e "${GREEN}✓ ${tag} built successfully${NC}"
    echo ""
}

# ── Main ────────────────────────────────────────────────────────────────────

# If no arguments, build all
if [ $# -eq 0 ]; then
    for entry in "${IMAGES[@]}"; do
        IFS=':' read -r lang dockerfile tag <<< "$entry"
        build_image "$lang" "$dockerfile" "$tag"
    done
    echo -e "${GREEN}All images built successfully.${NC}"
    exit 0
fi

# Otherwise build requested languages
for requested in "$@"; do
    found=false
    for entry in "${IMAGES[@]}"; do
        IFS=':' read -r lang dockerfile tag <<< "$entry"
        if [ "$lang" = "$requested" ]; then
            build_image "$lang" "$dockerfile" "$tag"
            found=true
            break
        fi
    done
    if [ "$found" = false ]; then
        echo -e "${RED}ERROR: Unknown language '${requested}'. Available: python${NC}"
        exit 1
    fi
done

echo -e "${GREEN}Done.${NC}"