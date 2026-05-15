from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    FastAPI Dependency — runs before every protected endpoint.
    If header is missing or doesn't match — returns 401.
    If valid — allows request to continue.
    """
    if not api_key or api_key != settings.api_key:
        logger.warning("Access attempt with invalid API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return api_key