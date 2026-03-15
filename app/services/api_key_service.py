import secrets
from datetime import datetime, timedelta,timezone
from sqlalchemy.orm import Session
from app.models.api_key import APIKey

def generate_api_key():
    return secrets.token_urlsafe(32)

def create_api_key(db: Session, user_id: int, scopes: str = "read", usage_limit: int = 1000, expires_days: int = 30):
    key = generate_api_key()
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)
    new_key = APIKey(
        key=key,
        user_id=user_id,
        scopes=scopes,
        usage_limit=usage_limit,
        expires_at=expires_at
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    return new_key

def revoke_api_key(db: Session, key_id: int):
    api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if api_key:
        api_key.is_active = False
        db.commit()
        return True
    return False