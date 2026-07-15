"""FastAPI app factory with CORS, static file serving, and all routers."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import FileResponse

from app.config import ALLOWED_ORIGINS
from app.database import check_database_integrity, create_tables
from app.routers import auth, exercises, lessons, progress

# Single source of truth for the app version
__version__ = "0.1.0"

# Whether we are in production mode
PRODUCTION = os.environ.get("PRODUCTION", "").lower() in ("1", "true", "yes")

# Path to the built frontend (relative to the api/ directory)
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup, seed dev users, and verify DB integrity."""
    await create_tables()

    # Always attempt to seed profile users — in production this is a no-op
    # if they already exist (the seed function checks before inserting).
    # This ensures the admin/dev user is present even if the DB was reset.
    from app.services.seed import ensure_profile_users

    created = await ensure_profile_users()
    if created:
        usernames = [u.username for u in created]
        print(f"[seed] Created profile users: {', '.join(usernames)}")
    elif not PRODUCTION:
        # In non-production mode, log that users already exist (normal case)
        pass
    else:
        # In production, verify the user table isn't empty
        try:
            integrity = await check_database_integrity()
            if integrity["ok"] and integrity.get("table_count", 0) == 0:
                print(
                    "[seed] WARNING: Database has no tables after startup — "
                    "this may indicate a fresh or corrupted database."
                )
        except Exception as e:
            print(f"[seed] WARNING: Could not verify database state: {e}")

    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Interactive Python Tutorials API",
        description="Backend for the Interactive Python Tutorials platform",
        version=__version__,
        docs_url="/docs" if not PRODUCTION else None,
        redoc_url="/redoc" if not PRODUCTION else None,
        lifespan=lifespan,
    )

    # CORS — in production the frontend is served by the same origin,
    # so we only need the wildcard for the tunnel domain, not localhost.
    if PRODUCTION:
        origins = ["*"]
    else:
        origins = ALLOWED_ORIGINS

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers (all mounted under /api prefix if they don't already have it)
    app.include_router(auth.router)
    app.include_router(lessons.router)
    app.include_router(exercises.router)
    app.include_router(progress.router)

    # Health check with database integrity verification
    @app.get("/api/health")
    async def health():
        integrity = await check_database_integrity()
        if not integrity["ok"]:
            from fastapi import status
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "database": integrity["message"],
                },
            )

        return {
            "status": "ok",
            "database": {
                "tables": integrity.get("table_count", 0),
                "size_bytes": integrity.get("size_bytes"),
            },
        }

    # Version endpoint
    @app.get("/api/version")
    async def version():
        return {"version": __version__}

    # In production mode, serve the built frontend as static files
    # and provide SPA fallback for client-side routing.
    if PRODUCTION:
        index_path = FRONTEND_DIST / "index.html"

        if FRONTEND_DIST.is_dir() and index_path.is_file():

            # Serve all static assets (JS, CSS, images) from /assets/
            app.mount(
                "/assets",
                StaticFiles(directory=str(FRONTEND_DIST / "assets")),
                name="frontend_assets",
            )

            # SPA catch-all — serve real files from dist/ directly
            # (favicon.svg, icons.svg, etc.) and fall back to index.html
            # for client-side routes (/lessons, /progress, /login, /).
            @app.route("/{path:path}", methods=["GET"])
            async def serve_spa(request, path: str = ""):
                # Let API paths fall through to their normal 404 handler
                if path.startswith("api/"):
                    raise StarletteHTTPException(status_code=404)

                # If the path matches a real file under dist, serve it
                file_path = FRONTEND_DIST / path if path else FRONTEND_DIST / "index.html"
                if file_path.exists() and file_path.is_file():
                    return FileResponse(str(file_path))

                # Otherwise serve index.html for client-side routing
                return FileResponse(str(index_path))

    return app


app = create_app()