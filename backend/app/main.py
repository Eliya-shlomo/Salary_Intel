from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.logging import get_logger
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from app.db.database import check_connection
from app.api.routes import router

logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
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