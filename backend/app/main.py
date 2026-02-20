import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.middleware.audit import AuditLogMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

# Routers
from app.auth.router import router as auth_router
from app.ingestion.router import router as ingestion_router
from app.assets.router import router as assets_router
from app.matching.router import router as matching_router
from app.ml.router import router as ml_router
from app.graph.router import router as graph_router
from app.risk.router import router as risk_router
from app.remediation.router import router as remediation_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("vulnguard")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 VulnGuard AI starting up...")
    await init_db()
    logger.info("✅ Database tables initialized")
    yield
    # Shutdown
    logger.info("👋 VulnGuard AI shutting down...")


app = FastAPI(
    title="SentinelX",
    description="Enterprise Exploit-Aware Vulnerability Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditLogMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=200, window_seconds=60)

# ── Routers ──
app.include_router(auth_router)
app.include_router(ingestion_router)
app.include_router(assets_router)
app.include_router(matching_router)
app.include_router(ml_router)
app.include_router(graph_router)
app.include_router(risk_router)
app.include_router(remediation_router)


# ── Health Check ──
@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "healthy",
        "service": "VulnGuard AI",
        "version": "1.0.0",
    }


@app.get("/api/dashboard/summary", tags=["Dashboard"])
async def dashboard_summary():
    """Aggregated dashboard summary — returns mock structure for frontend rendering."""
    from sqlalchemy import select, func
    from app.database import async_session
    from app.ingestion.models import CVE
    from app.assets.models import Asset
    from app.matching.models import VulnerabilityMatch
    from app.remediation.models import PatchJob, PatchStatus

    async with async_session() as db:
        total_cves = (await db.execute(select(func.count(CVE.id)))).scalar() or 0
        kev_count = (await db.execute(select(func.count(CVE.id)).where(CVE.is_kev == True))).scalar() or 0
        critical_cves = (await db.execute(
            select(func.count(CVE.id)).where(CVE.cvss_v3_score >= 9.0)
        )).scalar() or 0
        total_assets = (await db.execute(select(func.count(Asset.id)))).scalar() or 0
        total_matches = (await db.execute(select(func.count(VulnerabilityMatch.id)))).scalar() or 0
        open_matches = (await db.execute(
            select(func.count(VulnerabilityMatch.id)).where(VulnerabilityMatch.status == "open")
        )).scalar() or 0
        pending_patches = (await db.execute(
            select(func.count(PatchJob.id)).where(PatchJob.status == PatchStatus.PENDING_APPROVAL)
        )).scalar() or 0
        completed_patches = (await db.execute(
            select(func.count(PatchJob.id)).where(PatchJob.status == PatchStatus.COMPLETED)
        )).scalar() or 0

    return {
        "total_cves": total_cves,
        "kev_listed": kev_count,
        "critical_cves": critical_cves,
        "total_assets": total_assets,
        "total_vulnerabilities": total_matches,
        "open_vulnerabilities": open_matches,
        "pending_patches": pending_patches,
        "completed_patches": completed_patches,
    }
