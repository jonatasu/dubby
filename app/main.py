from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import logging
from .config import settings
from .routers import web, api

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    # Static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.mount("/outputs", StaticFiles(directory=str(settings.outputs_dir)), name="outputs")

    # Routers
    app.include_router(web.router)
    app.include_router(api.router, prefix="/api")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Initialize translation service on startup
    @app.on_event("startup")
    async def startup_event():
        try:
            from .services.translate import initialize_translation_service
            logger.info("Initializing translation service...")
            initialize_translation_service()
            logger.info("Translation service initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize translation service: {e}")
            logger.warning("Translation service will be initialized on first use")

    return app


app = create_app()
