import asyncio
import json
from datetime import datetime
from app.database import async_session
from sqlalchemy import select, delete
from app.auth.models import User
from app.assets.models import Asset
from app.ingestion.models import CVE
from app.remediation.models import PatchJob
from app.risk.models import RiskScore

async def seed():
    async with async_session() as db:
        
        # 1. Assets
        print("Seeding assets...")
        assets_data = [
            ("db-prod-aws-east", "linux", "ubuntu", "finance", "internal", False, 95, "critical"),
            ("api-gateway-v2", "linux", "debian", "engineering", "dmz", True, 82, "high"),
            ("eng-build-server", "linux", "ubuntu", "engineering", "internal", False, 75, "medium"),
            ("sales-crm-db", "windows", "windows server", "sales", "internal", False, 64, "low"),
            ("vpn-endpoint-nyc", "linux", "centos", "engineering", "dmz", True, 68, "high"),
            ("auth-service-02", "linux", "ubuntu", "engineering", "internal", False, 55, "medium"),
            ("internal-wiki", "linux", "debian", "hr", "internal", False, 42, "medium"),
            ("marketing-site", "linux", "ubuntu", "marketing", "dmz", True, 30, "low"),
        ]
        
        for h, plat, osn, bu, zone, is_int, score, crit in assets_data:
            res = await db.execute(select(Asset).where(Asset.hostname == h))
            if not res.scalar_one_or_none():
                db.add(Asset(
                    hostname=h,
                    os_platform=plat,
                    os_name=osn,
                    business_unit=bu,
                    network_zone=zone,
                    is_internet_facing=is_int,
                    risk_score=score,
                    criticality=crit,
                    agent_status='online',
                    ip_address=f"192.168.1.{random.randint(2, 254)}",
                    mac_address=f"00:1A:2B:3C:4D:{random.randint(10, 99)}",
                    open_ports=[80, 443]
                ))
        await db.commit()

        # 2. Patch Jobs
        print("Seeding patch jobs...")
        await db.execute(delete(PatchJob))
        res = await db.execute(select(Asset).limit(5))
        asset_rows = res.scalars().all()
        
        jobs = [
            ("CVE-2024-3094", "xz-utils", "5.4.1", "5.6.1", "CRITICAL", "[AI FIX] High probability of RCE detected via SSHD hooking. Recommend immediate update of xz-utils to 5.6.1 to close backdoor CVE-2024-3094.", "pending_approval"),
            ("CVE-2023-4863", "libwebp", "1.2.4", "1.3.2", "HIGH", "[AI FIX] Heap buffer overflow found in WebP compression. Exploit seen in the wild targeting browsers. Patch libwebp to prevent arbitrary code execution.", "pending_approval"),
            ("CVE-2023-38831", "winrar", "6.22", "6.23", "HIGH", "[AI FIX] Avoids arbitrary code execution from malicious ZIP archives. Detected highly vulnerable path; applying patch to update WinRAR components globally.", "approved"),
            ("CVE-2024-21412", "windows-kernel", "10.0.1", "10.0.2", "HIGH", "[AI FIX] Resolves Internet Shortcut Files Security Feature Bypass. Strongly recommended for internet-facing systems.", "completed")
        ]
        
        for i, (cid, pkg, cur_v, tgt_v, risk, desc, status) in enumerate(jobs):
            if i < len(asset_rows):
                db.add(PatchJob(
                    asset_id=asset_rows[i].id,
                    cve_id=cid,
                    package_name=pkg,
                    current_version=cur_v,
                    target_version=tgt_v,
                    risk_level=risk,
                    change_description=desc,
                    status=status,
                    requested_by=1
                ))
        await db.commit()

        # 3. Risk Scores
        print("Seeding risk scores...")
        await db.execute(delete(RiskScore))
        for i, row in enumerate(asset_rows):
            db.add(RiskScore(
                asset_id=row.id,
                cve_id='CVE-MOCK',
                risk_score=80 - i*5,
                risk_level='HIGH',
                breakdown_json=json.dumps({"factors": ["mock"]})
            ))
        await db.commit()

        # 4. CVEs
        print("Seeding CVEs...")
        await db.execute(delete(CVE).where(CVE.cve_id.in_(["CVE-2024-3094", "CVE-2023-4863", "CVE-2024-21412", "CVE-2023-38831", "CVE-2024-21338"])))
        cves = [
            ("CVE-2024-3094", "Critical backdoored xz-utils allow RCE.", 10.0, 0.94, True, True),
            ("CVE-2023-4863", "Heap buffer overflow in WebP.", 8.8, 0.88, True, True),
            ("CVE-2024-21412", "Internet Shortcut Files Security Feature Bypass", 8.1, 0.82, False, True),
            ("CVE-2023-38831", "WinRAR execution vulnerability", 7.8, 0.75, True, True),
            ("CVE-2024-21338", "Windows Kernel Privilege Escalation", 7.8, 0.61, False, True)
        ]
        for cid, desc, cvss, prob, has_exp, is_kev in cves:
            db.add(CVE(
                cve_id=cid, description=desc, cvss_v3_score=cvss, 
                predicted_exploit_probability=prob, has_public_exploit=has_exp, is_kev=is_kev,
                published_date=datetime.utcnow()
            ))
        await db.commit()
        print("Database seeded with AI mock data successfully using SQLAlchemy.")

import random
if __name__ == '__main__':
    asyncio.run(seed())
