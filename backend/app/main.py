from fastapi import FastAPI
from app.core.config import settings
from app.db.database import check_connection
from app.api.routes import router

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health_check():
    db_ok = check_connection()
    return {
        "status": "ok",
        "app": settings.app_name,
        "database": "connected" if db_ok else "error"
    }
