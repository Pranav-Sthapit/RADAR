
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.settings import get_settings
from .routers import get_map,get_route,detections


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Resolve paths relative to the backend directory,
    # rather than depending on the shell's working directory.
    backend_root = Path(__file__).resolve().parents[1]
    static_root = backend_root / "static"
    static_root.mkdir(parents=True, exist_ok=True)

    app.mount(
        "/static",
        StaticFiles(directory=static_root),
        name="static",
    )

    # Register the map router.
    # This assumes get_map is an APIRouter, not a function.
    app.include_router(get_map.router)
    app.include_router(get_route.router)
    app.include_router(detections.router)

    return app


app = create_app()
