from fastapi import FastAPI

from app.api.routes import metrics
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(metrics.router, prefix="/api/v1")
