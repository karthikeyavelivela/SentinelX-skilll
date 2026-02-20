from fastapi import APIRouter, Depends, Query
from app.auth.dependencies import get_current_user, require_role
from app.auth.models import User, UserRole
from app.graph.analysis import AttackPathAnalyzer
from app.graph.tasks import rebuild_graph

router = APIRouter(prefix="/api/graph", tags=["Attack Path Modeling"])

analyzer = AttackPathAnalyzer()


@router.get("/path/{source_id}/{target_id}")
async def get_shortest_path(
    source_id: int, target_id: int,
    current_user: User = Depends(get_current_user),
):
    """Find shortest attack path between two assets."""
    return await analyzer.shortest_path_to_asset(source_id, target_id)


@router.get("/lateral-movement/{asset_id}")
async def lateral_movement(
    asset_id: int,
    current_user: User = Depends(get_current_user),
):
    """Find lateral movement paths from an asset."""
    return await analyzer.lateral_movement_paths(asset_id)


@router.get("/blast-radius/{cve_id}")
async def blast_radius(
    cve_id: str,
    current_user: User = Depends(get_current_user),
):
    """Estimate blast radius of a vulnerability."""
    return await analyzer.blast_radius(cve_id)


@router.get("/risk-propagation")
async def risk_propagation(
    current_user: User = Depends(get_current_user),
):
    """Get risk propagation scores across the network."""
    return await analyzer.risk_propagation()


@router.get("/visualization")
async def graph_visualization(
    current_user: User = Depends(get_current_user),
):
    """Get full graph data for visualization."""
    return await analyzer.get_full_graph_data()


@router.post("/rebuild")
async def trigger_rebuild(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
):
    """Trigger graph rebuild."""
    task = rebuild_graph.delay()
    return {"status": "queued", "task_id": task.id}
