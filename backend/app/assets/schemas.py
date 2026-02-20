from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.assets.models import AssetCriticality, NetworkZoneType


class SoftwareItem(BaseModel):
    name: str
    vendor: Optional[str] = None
    version: Optional[str] = None
    cpe: Optional[str] = None
    is_service: bool = False
    service_status: Optional[str] = None
    service_port: Optional[int] = None


class ServiceItem(BaseModel):
    name: str
    display_name: Optional[str] = None
    pid: Optional[int] = None
    port: Optional[int] = None
    protocol: Optional[str] = None
    status: Optional[str] = None
    user: Optional[str] = None


class AssetCreate(BaseModel):
    hostname: str
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    os_platform: Optional[str] = None
    asset_type: Optional[str] = "server"
    criticality: AssetCriticality = AssetCriticality.MEDIUM
    network_zone: NetworkZoneType = NetworkZoneType.INTERNAL
    business_unit: Optional[str] = None
    owner: Optional[str] = None
    is_internet_facing: bool = False
    open_ports: List[int] = []
    tags: List[str] = []


class AssetResponse(BaseModel):
    id: int
    hostname: str
    ip_address: Optional[str]
    os_name: Optional[str]
    os_version: Optional[str]
    os_platform: Optional[str]
    asset_type: Optional[str]
    criticality: AssetCriticality
    network_zone: NetworkZoneType
    business_unit: Optional[str]
    is_internet_facing: bool
    open_ports: list
    agent_status: Optional[str]
    last_heartbeat: Optional[datetime]
    risk_score: float
    vulnerability_count: int
    tags: list
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    total: int
    items: List[AssetResponse]


class AgentRegistration(BaseModel):
    hostname: str
    agent_id: str
    agent_version: str
    os_name: str
    os_version: str
    os_platform: str
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    open_ports: List[int] = []
    installed_software: List[SoftwareItem] = []
    running_services: List[ServiceItem] = []
    user_privilege: Optional[str] = None
    patch_level: Optional[str] = None


class AgentHeartbeat(BaseModel):
    agent_id: str
    status: str = "online"
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
