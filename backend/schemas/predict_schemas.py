from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class NetworkInput(BaseModel):
    features: List[float] = Field(..., description="Array of network features")

class NetworkResponse(BaseModel):
    label: str
    confidence: float
    category: str

class AnomalyInput(BaseModel):
    features: List[float] = Field(..., description="Array of network features")

class AnomalyResponse(BaseModel):
    score: float
    label: str

class EmailInput(BaseModel):
    text: str = Field(..., description="Content of the email")

class EmailResponse(BaseModel):
    label: str
    confidence: float

class UrlInput(BaseModel):
    url: str = Field(..., description="URL to check")

class UrlResponse(BaseModel):
    label: str
    confidence: float
