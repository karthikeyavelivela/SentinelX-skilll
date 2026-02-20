import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, Enum as SAEnum, ForeignKey
from app.database import Base


class AssetCriticality(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NetworkZoneType(str, enum.Enum):
    DMZ = "dmz"
    INTERNAL = "internal"
    EXTERNAL = "external"
    RESTRICTED = "restricted"
    CLOUD = "cloud"


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(255), unique=True, index=True, nullable=False)
    ip_address = Column(String(45), index=True)
    mac_address = Column(String(17))
    os_name = Column(String(100))
    os_version = Column(String(100))
    os_platform = Column(String(50))  # windows, linux, macos
    
    # Classification
    asset_type = Column(String(50))  # server, workstation, network_device, container
    criticality = Column(SAEnum(AssetCriticality), default=AssetCriticality.MEDIUM)
    network_zone = Column(SAEnum(NetworkZoneType), default=NetworkZoneType.INTERNAL)
    business_unit = Column(String(100))
    owner = Column(String(255))
    
    # Network
    is_internet_facing = Column(Boolean, default=False)
    open_ports = Column(JSON, default=[])
    
    # Agent
    agent_id = Column(String(100), unique=True, nullable=True)
    agent_version = Column(String(20))
    last_heartbeat = Column(DateTime)
    agent_status = Column(String(20), default="unknown")  # online, offline, unknown
    
    # Patch level
    patch_level = Column(String(100))
    last_patched = Column(DateTime)
    pending_patches = Column(Integer, default=0)
    
    # Risk
    risk_score = Column(Float, default=0.0)
    vulnerability_count = Column(Integer, default=0)
    
    # Metadata
    tags = Column(JSON, default=[])
    custom_attributes = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InstalledSoftware(Base):
    __tablename__ = "installed_software"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True)
    name = Column(String(255), index=True)
    vendor = Column(String(255))
    version = Column(String(100))
    cpe = Column(String(500))  # CPE 2.3 string if known
    install_date = Column(DateTime)
    is_service = Column(Boolean, default=False)
    service_status = Column(String(20))  # running, stopped
    service_port = Column(Integer)


class RunningService(Base):
    __tablename__ = "running_services"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True)
    name = Column(String(255))
    display_name = Column(String(255))
    pid = Column(Integer)
    port = Column(Integer)
    protocol = Column(String(10))
    status = Column(String(20))
    user = Column(String(255))
