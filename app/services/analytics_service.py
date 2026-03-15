from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.request_log import RequestLog
from app.models.api_key import APIKey

def get_total_requests(db: Session):
    result = db.query(
        RequestLog.api_key,
        func.count(RequestLog.id).label("total_requests")
    ).group_by(RequestLog.api_key).all()
    return [{"api_key": r.api_key, "total_requests": r.total_requests} for r in result]

def get_top_endpoints(db: Session, limit: int = 5):
    result = db.query(
        RequestLog.endpoint,
        func.count(RequestLog.id).label("request_count")
    ).group_by(RequestLog.endpoint).order_by(func.count(RequestLog.id).desc()).limit(limit).all()
    return [{"endpoint": r.endpoint, "request_count": r.request_count} for r in result]

def get_suspicious_keys(db: Session):
    result = db.query(
        APIKey.key,
        func.count(RequestLog.id).label("request_count")
    ).join(RequestLog, APIKey.key == RequestLog.api_key)\
     .group_by(APIKey.key)\
     .having(func.count(RequestLog.id) > APIKey.usage_limit)\
     .all()
    return [{"api_key": r.key, "request_count": r.request_count} for r in result]