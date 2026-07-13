#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Building Docker sandbox images ==="

echo ""
echo "--- Building tutorial-runner-python:latest ---"
docker build -t tutorial-runner-python:latest "$SCRIPT_DIR/images/python"

echo ""
echo "=== All images built successfully ==="
docker images --filter=reference="tutorial-runner-*"