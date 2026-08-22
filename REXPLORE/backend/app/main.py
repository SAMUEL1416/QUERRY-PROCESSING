"""
ReXplore backend entrypoint.

Local:
    uvicorn app.main:app --reload

Production:
    uvicorn app.main:app --host 0.0.0.0 --port $PORT
"""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db
from routers import auth, papers, queries, datasets, analytics


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("rexplore")

settings = get_settings()

app = FastAPI(
    title="ReXplore API",
    description="Intelligent Semantic Research Understanding & Knowledge Discovery",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("ReXplore backend started. Database initialized.")


@app.get("/api/health", tags=["health"])
def health_check():
    return {
        "status": "ok",
        "service": "ReXplore API",
    }


# API routers
app.include_router(auth.router)
app.include_router(papers.router)
app.include_router(queries.router)
app.include_router(datasets.router)
app.include_router(analytics.router)


# ---------------------------------------------------------
# React frontend
# ---------------------------------------------------------

# PROJECT-FILE-REXPLORE/
# ├── backend/
# │   └── app/main.py
# └── frontend/
#     └── dist/
#
# main.py -> app -> backend -> PROJECT-FILE-REXPLORE
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

logger.info("Frontend directory: %s", FRONTEND_DIST)


@app.get("/", include_in_schema=False)
async def frontend_root():
    index_file = FRONTEND_DIST / "index.html"

    if not index_file.exists():
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Frontend has not been built yet."
            },
        )

    return FileResponse(index_file)


# Serve React static files
if FRONTEND_DIST.exists():
    app.mount(
        "/",
        StaticFiles(
            directory=str(FRONTEND_DIST),
            html=True,
        ),
        name="frontend",
    )