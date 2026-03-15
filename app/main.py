from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer
from app.routers import auth_router, api_keys_router, security_router, analytics_router
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.rate_limit_middleware import RateLimitMiddleware
from app.database import Base, engine
from app import models  # noqa: F401


security_scheme = HTTPBearer(auto_error=False)

app = FastAPI(
    title="SentinelAPI",
    debug=True,
    dependencies=[Depends(security_scheme)],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router.router)
app.include_router(api_keys_router.router)
app.include_router(security_router.router)
app.include_router(analytics_router.router)

app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)