import uuid
from sqlalchemy import Column, String, Float, JSON, DateTime
from sqlalchemy.sql import func
from core.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    module_name = Column(String, index=True) # network, log, phishing, malware, full
    threat_score = Column(Float, nullable=False)
    severity = Column(String, index=True) # LOW, MEDIUM, HIGH, CRITICAL
    severity_color = Column(String)
    module_scores = Column(JSON, default=dict)
    recommendations = Column(JSON, default=list)
    raw_input = Column(JSON, nullable=True)
    detailed_results = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
