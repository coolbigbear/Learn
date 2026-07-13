#!/usr/bin/env python3
"""
Production entry point for the Interactive Python Tutorials API.

Serves both the REST API and the built frontend static files
on a single port.  Run:

    uv run python run_prod.py

or (from the parent directory):

    cd api && uv run python run_prod.py

Requirements:
  - PRODUCTION=1 is set in the environment (this script forces it).
  - The frontend production build exists at ../frontend/dist/index.html
    (run `npm run build` in the frontend/ directory first).
"""

import os
import sys

# Force production mode
os.environ["PRODUCTION"] = "1"

# Ensure we can import from the api directory
_this_dir = os.path.dirname(os.path.abspath(__file__))
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

import uvicorn

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))

    print(f"  Starting production server on http://{host}:{port}")
    print(f"  PRODUCTION={os.environ['PRODUCTION']}")
    print()

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )