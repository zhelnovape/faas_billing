from fastapi import FastAPI

from app.api.routes import clients, functions, metrics, tariffs
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(clients.router, prefix="/api/v1")
app.include_router(tariffs.router, prefix="/api/v1")
app.include_router(functions.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")
