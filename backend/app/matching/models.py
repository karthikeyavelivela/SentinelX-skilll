from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.database import Base


class VulnerabilityMatch(Base):
    __tablename__ = "vulnerability_matches"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True)
    cve_id = Column(String(20), index=True)
    software_name = Column(String(255))
    software_version = Column(String(100))
    match_confidence = Column(Float)
    match_type = Column(String(50))  # exact_cpe, vendor_product, fuzzy
    cvss_score = Column(Float, default=0.0)
    
    # Status
    status = Column(String(20), default="open")  # open, patched, mitigated, accepted
    remediation_id = Column(Integer, nullable=True)
    
    matched_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
