import sqlite3
import random
from datetime import datetime

def seed():
    conn = sqlite3.connect('backend/vulnguard.db')
    c = conn.cursor()

    # 1. Update Asset "Karthikeya" -> "core-router-01"
    c.execute('UPDATE assets SET hostname="core-router-01", business_unit="engineering", network_zone="dmz", is_internet_facing=1, risk_score=88 WHERE hostname="Karthikeya"')
    
    # 2. Insert new assets if they don't exist
    assets = [
        ("db-prod-aws-east", "linux", "ubuntu", "finance", "internal", 0, 95, "critical"),
        ("api-gateway-v2", "linux", "debian", "engineering", "dmz", 1, 82, "high"),
        ("eng-build-server", "linux", "ubuntu", "engineering", "internal", 0, 75, "medium"),
        ("sales-crm-db", "windows", "windows server", "sales", "internal", 0, 64, "low"),
        ("vpn-endpoint-nyc", "linux", "centos", "engineering", "dmz", 1, 68, "high")
    ]
    
    c.execute("SELECT MAX(id) FROM assets")
    max_id = c.fetchone()[0] or 1
    
    for h, plat, osn, bu, zone, is_int, score, crit in assets:
        c.execute("SELECT id FROM assets WHERE hostname=?", (h,))
        if not c.fetchone():
            max_id += 1
            c.execute("""
                INSERT INTO assets (id, hostname, os_platform, os_name, business_unit, network_zone, is_internet_facing, risk_score, criticality, agent_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'online', CURRENT_TIMESTAMP)
            """, (max_id, h, plat, osn, bu, zone, is_int, score, crit))

    # 3. Insert Remediation Patch Jobs with "AI-like" descriptions
    c.execute("DELETE FROM patch_jobs") # clear existing mock jobs if any
    c.execute("SELECT id, hostname FROM assets LIMIT 5")
    asset_rows = c.fetchall()
    
    jobs = [
        ("CVE-2024-3094", "xz-utils", "5.4.1", "5.6.1", "CRITICAL", 
         "[AI FIX] High probability of RCE detected via SSHD hooking. Recommend immediate update of xz-utils to 5.6.1 to close backdoor CVE-2024-3094.", "pending_approval"),
        ("CVE-2023-4863", "libwebp", "1.2.4", "1.3.2", "HIGH", 
         "[AI FIX] Heap buffer overflow found in WebP compression. Exploit seen in the wild targeting browsers. Patch libwebp to prevent arbitrary code execution.", "pending_approval"),
        ("CVE-2023-38831", "winrar", "6.22", "6.23", "HIGH", 
         "[AI FIX] Avoids arbitrary code execution from malicious ZIP archives. Detected highly vulnerable path; applying patch to update WinRAR components globally.", "approved")
    ]
    
    job_id = 1
    for i, j in enumerate(jobs):
        if i >= len(asset_rows): break
        asset_id, asset_host = asset_rows[i]
        c.execute("""
            INSERT INTO patch_jobs (id, asset_id, cve_id, package_name, current_version, target_version, risk_level, change_description, status, created_at, requested_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
        """, (job_id, asset_id, j[0], j[1], j[2], j[3], j[4], j[5], j[6]))
        job_id += 1

    # 4. Insert Risk Scores matching the mock data fallback
    c.execute("DELETE FROM risk_scores")
    for i, row in enumerate(asset_rows):
        c.execute("""
            INSERT INTO risk_scores (asset_id, cve_id, risk_score, risk_level, breakdown_json, calculated_at)
            VALUES (?, 'CVE-MOCK', ?, 'HIGH', '{"factors": ["mock"]}', CURRENT_TIMESTAMP)
        """, (row[0], 80 - i*5))

    # 5. Insert CVEs with predicted exploit probability so ML predictions feature live data
    c.execute("DELETE FROM cves WHERE cve_id LIKE 'CVE-2024-%' OR cve_id LIKE 'CVE-2023-%'")
    cves = [
        ("CVE-2024-3094", "Critical backdoored xz-utils allow RCE.", 10.0, 0.94, 1, 1),
        ("CVE-2023-4863", "Heap buffer overflow in WebP.", 8.8, 0.88, 1, 1),
        ("CVE-2024-21412", "Internet Shortcut Files Security Feature Bypass", 8.1, 0.82, 0, 1),
        ("CVE-2023-38831", "WinRAR execution vulnerability", 7.8, 0.75, 1, 1),
        ("CVE-2024-21338", "Windows Kernel Privilege Escalation", 7.8, 0.61, 0, 1)
    ]
    for cid, desc, cvss, prob, has_exp, is_kev in cves:
        c.execute("""
            INSERT INTO cves (cve_id, description, cvss_v3_score, predicted_exploit_probability, has_public_exploit, is_kev, published_date)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (cid, desc, cvss, prob, has_exp, is_kev))

    conn.commit()
    conn.close()
    print("Database seeded with AI mock data successfully.")

if __name__ == '__main__':
    seed()
