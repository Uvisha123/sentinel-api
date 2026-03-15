from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.rate_limiter import check_rate_limit
from app.services.security_engine import detect_suspicious_activity


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow docs, OpenAPI schema, and auth routes without API key.
        # Also allow creating the first API key without already having one.
        if (
            request.url.path in {"/docs", "/redoc", "/openapi.json"}
            or request.url.path.startswith("/auth")
            or (request.url.path.startswith("/api-keys") and request.method == "POST")
        ):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "API key missing"},
            )

        db: Session = SessionLocal()
        try:
            allowed = check_rate_limit(db, api_key)
            if not allowed:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded"},
                )

            detect_suspicious_activity(db, api_key, request.client.host)
        finally:
            db.close()

        response = await call_next(request)
        return response