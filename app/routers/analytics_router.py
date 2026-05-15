from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.analytics_service import get_total_requests, get_top_endpoints, get_suspicious_keys

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/requests")
def total_requests(
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    return get_total_requests(db)

@router.get("/top-endpoints")
def top_endpoints(
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    return get_top_endpoints(db)

@router.get("/abuse-detection")
def abuse_detection(
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    return get_suspicious_keys(db)