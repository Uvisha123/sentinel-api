from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime,timezone
from app.database import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(128))
    endpoint = Column(String)
    ip_address = Column(String)
    method = Column(String)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))