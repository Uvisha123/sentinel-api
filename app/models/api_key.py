from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Boolean
from datetime import datetime,timezone,timedelta
from sqlalchemy.orm import relationship
from app.database import Base

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    scopes = Column(String, default="read")  # e.g., read, write, admin
    usage_limit = Column(Integer, default=1000)  # per day/hour
    expires_at = Column(DateTime, default=datetime.now(timezone.utc) + timedelta(days=30))
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="api_keys")