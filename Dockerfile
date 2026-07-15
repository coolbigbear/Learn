# =============================================================================
# Multi-stage Dockerfile for the Interactive Python Tutorials platform
#
# Stage 1 — Build the React frontend (Vite)
# Stage 2 — Python runtime serving both API and static frontend
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: frontend-builder — compile the Vite/React SPA
# ---------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /build

# Install dependencies first (layer caching)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy the rest of the frontend source and build
COPY frontend/ ./
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: runtime — Python 3.13-slim running FastAPI + Uvicorn
# ---------------------------------------------------------------------------
FROM python:3.13-slim

WORKDIR /app

# ── Environment ──────────────────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ── System dependencies ──────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ── Data directory for the SQLite database (persisted via named volume) ──────
RUN mkdir -p /app/data

# ── Python dependencies (layer caching) ──────────────────────────────────────
COPY api/requirements.txt api/pyproject.toml /app/
RUN pip install --no-cache-dir -r requirements.txt

# ── API source code ──────────────────────────────────────────────────────────
COPY api/ /app/

# ── Built frontend (from Stage 1) ────────────────────────────────────────────
# FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
# With the API at /app/api/ this resolves to /app/frontend/dist/
COPY --from=frontend-builder /build/dist /app/frontend/dist

# ── Runtime ──────────────────────────────────────────────────────────────────
EXPOSE 8080

# All configuration is driven by environment variables (PRODUCTION, DATABASE_URL, etc.)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]