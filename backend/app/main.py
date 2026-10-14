from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.logging import get_logger
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from app.db.database import check_connection
from app.api.routes import router
from app.api.pipeline_routes import router as pipeline_router
from app.api.analyst_routes import router as analyst_router
from fastapi.responses import JSONResponse

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
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
app.include_router(pipeline_router, prefix="/api/v1")
app.include_router(analyst_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    try:
        check_connection()
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "app": settings.app_name,
                "database": "error",
            },
        )
    return {
        "status": "ok",
        "app": settings.app_name,
        "database": "connected",
    }