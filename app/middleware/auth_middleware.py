from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.auth_service import decode_access_token


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Public/auth routes and docs should be accessible without token
        if request.url.path.startswith("/auth") or request.url.path in {
            "/docs",
            "/redoc",
            "/openapi.json",
        }:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid token"},
            )

        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        if not payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"},
            )

        request.state.user = payload.get("sub")
        response = await call_next(request)
        return response