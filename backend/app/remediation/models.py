import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, Enum as SAEnum, ForeignKey
from app.database import Base


class PatchStatus(str, enum.Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    DRY_RUN_COMPLETE = "dry_run_complete"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class PatchJob(Base):
    __tablename__ = "patch_jobs"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True)
    cve_id = Column(String(20), index=True)
    
    # Patch details
    patch_type = Column(String(50))  # os_update, package_update, config_change
    platform = Column(String(20))   # linux, windows
    package_name = Column(String(255))
    current_version = Column(String(100))
    target_version = Column(String(100))
    
    # Status
    status = Column(String(50), default=PatchStatus.PENDING_APPROVAL.value)
    is_dry_run = Column(Boolean, default=True)
    
    # Execution
    script_content = Column(Text)
    execution_log = Column(Text)
    rollback_script = Column(Text)
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    maintenance_window_start = Column(DateTime, nullable=True)
    maintenance_window_end = Column(DateTime, nullable=True)
    
    # Approval
    requested_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Change log
    change_description = Column(Text)
    risk_level = Column(String(20))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
