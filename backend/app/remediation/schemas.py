from pydantic import BaseModel
from typing import Optional, List
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
    patch_type: str
    platform: Optional[str]
    package_name: str
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

    class Config:
        from_attributes = True


class PatchApproval(BaseModel):
    approved: bool
    notes: Optional[str] = None


class PatchSchedule(BaseModel):
    scheduled_at: datetime
    maintenance_window_start: datetime
    maintenance_window_end: datetime
