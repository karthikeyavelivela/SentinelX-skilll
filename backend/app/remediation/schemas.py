from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
from datetime import datetime
from app.remediation.models import PatchStatus


class PatchJobCreate(BaseModel):
    asset_id: int
    cve_id: str
    patch_type: str = "package_update"
    package_name: str
    current_version: Optional[str] = None
    target_version: Optional[str] = None
    is_dry_run: bool = True
    change_description: Optional[str] = None
    maintenance_window_start: Optional[datetime] = None
    maintenance_window_end: Optional[datetime] = None


class PatchJobResponse(BaseModel):
    id: int
    asset_id: int
    cve_id: str
    patch_type: Optional[str]
    platform: Optional[str]
    package_name: Optional[str]
    current_version: Optional[str]
    target_version: Optional[str]
    status: PatchStatus
    is_dry_run: bool
    script_content: Optional[str]
    execution_log: Optional[str]
    rollback_script: Optional[str]
    risk_level: Optional[str]
    change_description: Optional[str]
    scheduled_at: Optional[datetime]
    created_at: Optional[datetime]
    completed_at: Optional[datetime]

    @field_validator("is_dry_run", mode="before")
    def parse_is_dry_run(cls, v):
        if v is None:
            return True
        return v

    @field_validator("status", mode="before")
    def parse_status(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

    class Config:
        from_attributes = True


class PatchApproval(BaseModel):
    approved: bool
    notes: Optional[str] = None


class PatchSchedule(BaseModel):
    scheduled_at: datetime
    maintenance_window_start: datetime
    maintenance_window_end: datetime
