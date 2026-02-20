from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from app.database import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True)
    cve_id = Column(String(20), index=True, nullable=True)  # null = asset-level score
    
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20))
    
    # Breakdown
    exploit_probability_factor = Column(Float)
    criticality_factor = Column(Float)
    attack_path_factor = Column(Float)
    exposure_factor = Column(Float)
    business_impact_factor = Column(Float)
    urgency_boost = Column(Float, default=1.0)
    
    breakdown_json = Column(JSON)
    
    calculated_at = Column(DateTime, default=datetime.utcnow)
