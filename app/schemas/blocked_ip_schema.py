from pydantic import BaseModel
from datetime import datetime


class BlockedIPCreate(BaseModel):
    ip_address: str
    reason: str


class BlockedIPRead(BaseModel):
    id: int
    ip_address: str
    reason: str
    blocked_at: datetime

    class Config:
        orm_mode = True