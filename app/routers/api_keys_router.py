from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.api_key import APIKey
from app.schemas.api_key_schema import APIKeyCreate,APIKeyRead
from app.services.security_engine import generate_api_key

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=APIKeyRead)
def create_api_key(data: APIKeyCreate, db: Session = Depends(get_db)):
    new_key = APIKey(
        key=generate_api_key(),
        user_id=data.user_id,
        scopes=data.scopes or "read",
        usage_limit=data.usage_limit or 1000,
        expires_at=data.expires_at,
    )

    db.add(new_key)
    db.commit()
    db.refresh(new_key)

    return new_key


@router.get("/", response_model=list[APIKeyRead])
def list_api_keys(
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    keys = db.query(APIKey).all()
    return keys


@router.delete("/{key_id}")
def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    key = db.query(APIKey).filter(APIKey.id == key_id).first()

    if not key:
        raise HTTPException(status_code=404, detail="Key not found")

    db.delete(key)
    db.commit()

    return {"message": "API key deleted"}