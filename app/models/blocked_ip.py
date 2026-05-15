from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime,timezone
from app.database import Base


class BlockedIP(Base):
    __tablename__ = "blocked_ips"

    id = Column(Integer, primary_key=True)
    ip_address = Column(String, unique=True, nullable=False)
    reason = Column(String)
    blocked_at = Column(DateTime, default=datetime.now(timezone.utc) )