from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime,timezone
from app.database import Base

class RateLimit(Base):
    __tablename__ = "rate_limits"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String, nullable=False)
    request_count = Column(Integer, default=0)
    window_start = Column(DateTime, default=datetime.now(timezone.utc))
    window_duration = Column(Integer, default=60)  # seconds