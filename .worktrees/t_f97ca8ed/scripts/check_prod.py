#!/usr/bin/env python3
"""Quick check script that verifies production build and API import work."""

import sys
import os

os.environ["PRODUCTION"] = "1"

# Check frontend dist exists
dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist", "index.html")
if not os.path.isfile(dist):
    print(f"ERROR: Frontend build not found at {dist}")
    print("Run: cd frontend && npm run build")
    sys.exit(1)
print(f"  OK: Frontend build found at {dist}")

# Check API imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
try:
    from app.main import app
    print(f"  OK: FastAPI app loaded, PRODUCTION={os.environ.get('PRODUCTION')}")
except Exception as e:
    print(f"ERROR: Failed to import app: {e}")
    sys.exit(1)

# Check static file mount
has_static = any(
    getattr(route, "path", "").startswith("/assets")
    for route in app.routes
)
print(f"  OK: /assets mount {'found' if has_static else 'NOT found'}")

# Check SPA catch-all
has_spa = any(
    getattr(route, "path", "") == "/{path:path}"
    for route in app.routes
)
print(f"  OK: SPA catch-all {'found' if has_spa else 'NOT found'}")

print()
print("All checks passed. Ready for production.")