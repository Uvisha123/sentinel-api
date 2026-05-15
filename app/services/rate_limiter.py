from datetime import datetime, timedelta, timezone

from datetime import datetime, timedelta,timezone

from sqlalchemy.orm import Session
from app.models.rate_limit import RateLimit

REQUEST_LIMIT = 100
TIME_WINDOW = 60
TIME_WINDOW = 60  



def check_rate_limit(db: Session, api_key: str):
    from app.models.api_key import APIKey
    key_obj = db.query(APIKey).filter(
        APIKey.key == api_key,
        APIKey.is_active == True
    ).first()

    if not key_obj:
        return False

