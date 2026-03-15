from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.rate_limit import RateLimit

REQUEST_LIMIT = 100
TIME_WINDOW = 60  


def check_rate_limit(db: Session, api_key: str):
    """
    Rate limit per API key using its usage_limit
    """
    from app.models.api_key import APIKey
    key_obj = db.query(APIKey).filter(APIKey.key == api_key, APIKey.is_active == True).first()
    if not key_obj:
        return False  

    # Use naive UTC time to match stored datetimes
    now = datetime.utcnow()
    rate = db.query(RateLimit).filter(RateLimit.api_key == api_key).first()

    if not rate:
        rate = RateLimit(api_key=api_key, request_count=1, window_start=now)
        db.add(rate)
        db.commit()
        return True

    window_end = rate.window_start + timedelta(seconds=rate.window_duration)
    if now > window_end:
        rate.request_count = 1
        rate.window_start = now
        db.commit()
        return True
    else:
        rate.request_count += 1
        db.commit()
        if rate.request_count > key_obj.usage_limit:
            return False  
        return True