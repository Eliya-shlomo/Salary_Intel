from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    client_ip = get_remote_address(request)
    logger.warning(f"Rate limit חרג | IP: {client_ip}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": "יותר מדי בקשות. נסה שוב בעוד דקה.",
            "retry_after": "60 seconds"
        }
    )