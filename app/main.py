from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import settings
from .routers import web, api


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

    return app


app = create_app()
