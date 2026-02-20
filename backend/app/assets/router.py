from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.auth.models import User, UserRole
from app.assets.models import Asset, InstalledSoftware, RunningService
from app.assets.schemas import (
    AssetCreate, AssetResponse, AssetListResponse,
    AgentRegistration, AgentHeartbeat, SoftwareItem, ServiceItem,
)

router = APIRouter(prefix="/api/assets", tags=["Asset Inventory"])


@router.get("", response_model=AssetListResponse)
async def list_assets(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    business_unit: Optional[str] = None,
    criticality: Optional[str] = None,
    network_zone: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Asset)
    if business_unit:
        query = query.where(Asset.business_unit == business_unit)
    if criticality:
        query = query.where(Asset.criticality == criticality)
    if network_zone:
        query = query.where(Asset.network_zone == network_zone)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(Asset.risk_score.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return AssetListResponse(total=total, items=result.scalars().all())


@router.post("", response_model=AssetResponse, status_code=201)
async def create_asset(
    asset_data: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
):
    asset = Asset(**asset_data.model_dump())
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(404, "Asset not found")
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int, asset_data: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(404, "Asset not found")
    for k, v in asset_data.model_dump().items():
        setattr(asset, k, v)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(
    asset_id: int, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(404, "Asset not found")
    await db.delete(asset)
    await db.commit()


# ── Agent Endpoints ──

@router.post("/agent/register", response_model=AssetResponse)
async def register_agent(
    registration: AgentRegistration,
    db: AsyncSession = Depends(get_db),
):
    # Upsert by agent_id
    result = await db.execute(select(Asset).where(Asset.agent_id == registration.agent_id))
    asset = result.scalar_one_or_none()

    if asset:
        asset.os_name = registration.os_name
        asset.os_version = registration.os_version
        asset.os_platform = registration.os_platform
        asset.ip_address = registration.ip_address
        asset.open_ports = registration.open_ports
        asset.agent_version = registration.agent_version
        asset.last_heartbeat = datetime.utcnow()
        asset.agent_status = "online"
        asset.patch_level = registration.patch_level
    else:
        asset = Asset(
            hostname=registration.hostname,
            agent_id=registration.agent_id,
            agent_version=registration.agent_version,
            os_name=registration.os_name,
            os_version=registration.os_version,
            os_platform=registration.os_platform,
            ip_address=registration.ip_address,
            mac_address=registration.mac_address,
            open_ports=registration.open_ports,
            last_heartbeat=datetime.utcnow(),
            agent_status="online",
            patch_level=registration.patch_level,
        )
        db.add(asset)

    await db.commit()
    await db.refresh(asset)

    # Store software inventory
    if registration.installed_software:
        for sw in registration.installed_software:
            db.add(InstalledSoftware(asset_id=asset.id, **sw.model_dump()))
    if registration.running_services:
        for svc in registration.running_services:
            db.add(RunningService(asset_id=asset.id, **svc.model_dump()))
    await db.commit()

    return asset


@router.post("/agent/heartbeat")
async def agent_heartbeat(
    heartbeat: AgentHeartbeat,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Asset).where(Asset.agent_id == heartbeat.agent_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(404, "Agent not registered")
    asset.last_heartbeat = datetime.utcnow()
    asset.agent_status = heartbeat.status
    await db.commit()
    return {"status": "ok"}
