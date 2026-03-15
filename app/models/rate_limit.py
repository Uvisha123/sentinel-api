from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base


class RateLimit(Base):
    __tablename__ = "rate_limits"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String, nullable=False)
    request_count = Column(Integer, default=0)
    # Use naive UTC datetimes to avoid offset-aware vs offset-naive comparisons
    window_start = Column(DateTime, default=datetime.utcnow)
    window_duration = Column(Integer, default=60)  # seconds