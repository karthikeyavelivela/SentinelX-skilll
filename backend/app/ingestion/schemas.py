from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CVEResponse(BaseModel):
    id: int
    cve_id: str
    description: Optional[str]
    published_date: Optional[datetime]
    cvss_v3_score: float
    cvss_v3_severity: Optional[str]
    attack_vector: Optional[str]
    attack_complexity: Optional[str]
    privileges_required: Optional[str]
    vendor: Optional[str]
    product: Optional[str]
    epss_score: float
    epss_percentile: float
    is_kev: bool
    has_public_exploit: bool
    exploit_maturity: Optional[str]
    predicted_exploit_probability: float
    prediction_confidence: float

    class Config:
        from_attributes = True


class CVEListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[CVEResponse]


class CVESearchQuery(BaseModel):
    keyword: Optional[str] = None
    vendor: Optional[str] = None
    product: Optional[str] = None
    min_cvss: Optional[float] = None
    max_cvss: Optional[float] = None
    is_kev: Optional[bool] = None
    has_exploit: Optional[bool] = None
    severity: Optional[str] = None
    page: int = 1
    per_page: int = 25


class IngestionStatusResponse(BaseModel):
    source: str
    status: str
    records_processed: int
    last_ingested: Optional[datetime]
    message: Optional[str]


class ExploitResponse(BaseModel):
    id: int
    cve_id: str
    source: str
    source_url: Optional[str]
    title: Optional[str]
    exploit_type: Optional[str]
    platform: Optional[str]
    verified: bool
    maturity: str

    class Config:
        from_attributes = True
