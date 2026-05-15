from pydantic import BaseModel
from datetime import datetime


class RateLimitRead(BaseModel):
    id: int
    api_key: str
    request_count: int
    window_start: datetime
    window_duration: int

    class Config:
        orm_mode = True