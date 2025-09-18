from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import logging
from .config import settings
from .routers import web, api
from .services.translate import initialize_translation_service

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Initializing translation service (lifespan)...")
        initialize_translation_service()
        logger.info("Translation service initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize translation service: {e}")
        logger.warning("Translation service will be initialized on first use")
    yield
    # (Optional) teardown logic


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

    # Static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.mount("/outputs", StaticFiles(directory=str(settings.outputs_dir)), name="outputs")

    # Routers
    app.include_router(web.router)
    app.include_router(api.router, prefix="/api")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
