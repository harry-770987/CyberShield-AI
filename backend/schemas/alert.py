from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class ThreatReport(BaseModel):
    final_threat_score: float
    severity: str
    severity_color: str
    module_scores: Dict[str, float]
    recommendations: List[str]
    timestamp: str
    session_id: str
    detailed_results: Optional[Dict[str, Any]] = None

class NetworkAnalysisRequest(BaseModel):
    features: Dict[str, Any]

class PhishingRequest(BaseModel):
    url: str
    email_body: Optional[str] = ""

class AlertResponse(BaseModel):
    id: str
    module_name: str
    threat_score: float
    severity: str
    severity_color: str
    module_scores: Dict[str, float]
    recommendations: List[str]
    raw_input: Optional[Dict[str, Any]]
    detailed_results: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_alerts: int
    critical_today: int
    avg_threat_score_today: float
    by_severity: Dict[str, int]
    by_module: Dict[str, int]
    alerts_last_7_days: List[Dict[str, Any]]
    top_threat_today: float
