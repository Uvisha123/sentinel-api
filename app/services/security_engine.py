from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.request_log import RequestLog
from app.models.blocked_ip import BlockedIP
from app.models.api_key import APIKey

MAX_REQUESTS_PER_MINUTE = 100
FAILED_LOGIN_THRESHOLD = 5


def generate_api_key(length: int = 32) -> str:
    return token_urlsafe(length)


def detect_suspicious_activity(db: Session, api_key: str, ip_address: str):
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=1)

    
    recent_requests = db.query(RequestLog).filter(
        RequestLog.api_key == api_key,
        RequestLog.timestamp >= window_start
    ).count()

    if recent_requests > MAX_REQUESTS_PER_MINUTE:
        block_ip(db, ip_address, reason="Request flood detected")
        return True

    return False

def flag_suspicious_requests(db: Session):
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=1)

    suspicious = db.query(
        APIKey.key,
        func.count(RequestLog.id).label("req_count")
    ).join(RequestLog, APIKey.key == RequestLog.api_key)\
     .filter(RequestLog.timestamp >= window_start)\
     .group_by(APIKey.key)\
     .having(func.count(RequestLog.id) > APIKey.usage_limit)\
     .all()

    return [{"api_key": r.key, "request_count": r.req_count} for r in suspicious]

def block_ip(db: Session, ip_address: str, reason: str):
    existing = db.query(BlockedIP).filter(BlockedIP.ip_address == ip_address).first()
    if existing:
        return

    blocked = BlockedIP(ip_address=ip_address, reason=reason)
    db.add(blocked)
    db.commit()
    
def calculate_anomaly_score(db: Session, api_key: str, ip_address: str):
    """
    Simple anomaly scoring:
    - High request bursts = +50
    - Multiple failed logins = +30
    - Multiple IPs for same key = +20
    """
    score = 0
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=1)

    recent_requests = db.query(RequestLog).filter(
        RequestLog.api_key == api_key,
        RequestLog.timestamp >= window_start
    ).count()
    if recent_requests > 50:
        score += 50

   
    return score    