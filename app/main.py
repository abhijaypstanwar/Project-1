from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database import create_tables
from app.routers import auth as auth_router
from app.routers import admin as admin_router

# Base directory = wherever main.py lives
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup():
        import app.models
        create_tables()

    # ── static files ──
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(BASE_DIR, "static")),
        name="static",
    )

    # ── page routes ──
    @app.get("/")
    def serve_welcome():
        return FileResponse(os.path.join(BASE_DIR, "welcome.html"))

    @app.get("/welcome")
    def serve_welcome2():
        return FileResponse(os.path.join(BASE_DIR, "welcome.html"))

    @app.get("/login")
    def serve_login():
        return FileResponse(os.path.join(BASE_DIR, "index.html"))

    @app.get("/admin")
    def serve_admin():
        return FileResponse(os.path.join(BASE_DIR, "admin.html"))

    # ── api routers ──
    app.include_router(auth_router.router)
    app.include_router(admin_router.router)

    # ── health ──
    @app.get("/health", tags=["Health"])
    def health():
        return {"status": "ok", "app": settings.APP_NAME}

    # ── swagger bearer auth ──
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=settings.APP_NAME,
            version="0.1.0",
            routes=app.routes,
        )
        schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
        for path in schema["paths"].values():
            for method in path.values():
                method["security"] = [{"BearerAuth": []}]
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi

    return app


app = create_app()