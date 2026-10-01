"""API-key authentication dependency."""

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings

security = HTTPBearer(auto_error=False)


async def get_api_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str | None:
    """
    Authenticate requests via API key.

    - If settings.api_key is empty → dev mode, no auth required (returns None).
    - Otherwise, the client must provide the key via:
        X-API-Key header, OR
        Authorization: Bearer <key>, OR
        ?api_key= query param (for SSE / EventSource)
    """
    if not settings.api_key:
        return None  # Dev mode — auth disabled

    provided = None

    # Check X-API-Key header first
    provided = request.headers.get("X-API-Key")

    # Fall back to Authorization: Bearer
    if not provided and credentials:
        provided = credentials.credentials

    # Fall back to query param (for SSE EventSource which can't set custom headers)
    if not provided:
        provided = request.query_params.get("api_key")

    if not provided or provided != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return provided
