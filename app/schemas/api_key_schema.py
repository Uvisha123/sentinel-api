from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class APIKeyCreate(BaseModel):
    user_id: int
    scopes: Optional[str] = "read"
    usage_limit: Optional[int] = 1000
    expires_at: Optional[datetime] = None


class APIKeyRead(BaseModel):
    id: int
    key: str
    user_id: int
    scopes: str
    usage_limit: int
    expires_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

APIKeyOut = APIKeyRead