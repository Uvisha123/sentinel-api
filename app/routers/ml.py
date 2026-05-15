from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.services.ml_service import (
    score_ip,
    cluster_ip,
    get_models_status,
    reload_models,
    startup_load_models,
)


class IPFeaturesRequest(BaseModel):
    requests_per_min: float = Field(..., ge=0, description="Average requests per minute from this IP")
    endpoint_variety: int = Field(..., ge=1, description="Number of unique endpoints accessed")
    error_rate: float = Field(..., ge=0, le=1, description="Fraction of error responses (0.0 to 1.0)")
    avg_time_between_reqs: float = Field(..., ge=0, description="Average seconds between consecutive requests")
    single_endpoint_ratio: float = Field(..., ge=0, le=1,description="Fraction of requests to most-hit endpoint (0.0 to 1.0)")
    user_agent_variety: int = Field(..., ge=1, description="Number of distinct user agents used")

    class Config:
        json_schema_extra = {
            "example": {
                "requests_per_min": 3.5,
                "endpoint_variety": 2,
                "error_rate": 0.85,
                "avg_time_between_reqs": 15.0,
                "single_endpoint_ratio": 0.90,
                "user_agent_variety": 1,
            }
        }


class RiskScoreResponse(BaseModel):
    """Response from /ml/score endpoint."""
    anomaly: bool
    anomaly_score: float
    cluster_id: int
    cluster_label: str
    risk_probability: float
    risk_tier: str
    recommendation: str


class ClusterResponse(BaseModel):
    """Response from /ml/cluster endpoint."""
    cluster_id: int
    cluster_label: str
    anomaly: bool
    anomaly_score: float
    risk_probability: float
    risk_tier: str
    profile: str
    description: str
    suggested_action: str
    input_features: dict


class StatusResponse(BaseModel):
    """Response from /ml/status endpoint."""
    models_loaded: bool
    feature_columns: list
    risk_thresholds: dict



router = APIRouter(
    prefix="/ml",
    tags=["Machine Learning"],
    responses={ 503: {"description": "ML models not loaded"},}, )



@router.post("/score", response_model=RiskScoreResponse)
def score_ip_endpoint(request: IPFeaturesRequest):
    try:
        features = request.model_dump()
        result = score_ip(features)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cluster", response_model=ClusterResponse)
def cluster_ip_endpoint(request: IPFeaturesRequest):
    try:
        features = request.model_dump()
        result = cluster_ip(features)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status", response_model=StatusResponse)
def ml_status_endpoint():
    return get_models_status()


@router.post("/reload")
def reload_models_endpoint():
    try:
        result = reload_models()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
