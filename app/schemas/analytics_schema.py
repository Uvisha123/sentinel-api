from pydantic import BaseModel


class RequestCount(BaseModel):
    total_requests: int


class TopEndpoint(BaseModel):
    endpoint: str
    request_count: int


class TopAPIKey(BaseModel):
    api_key: str
    request_count: int