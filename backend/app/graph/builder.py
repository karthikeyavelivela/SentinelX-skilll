import logging
from typing import List, Dict
from app.graph.neo4j_client import neo4j_client

logger = logging.getLogger("vulnguard.graph.builder")


class GraphBuilder:
    """Build and maintain the attack graph in Neo4j."""

    async def clear_graph(self):
        """Clear all nodes and relationships."""
        await neo4j_client.run_write("MATCH (n) DETACH DELETE n")
        logger.info("Graph cleared")

    async def build_asset_nodes(self, assets: List[Dict]):
        """Create asset nodes."""
        query = """
        UNWIND $assets AS asset
        MERGE (a:Asset {asset_id: asset.id})
        SET a.hostname = asset.hostname,
            a.ip_address = asset.ip_address,
            a.os_platform = asset.os_platform,
            a.criticality = asset.criticality,
            a.network_zone = asset.network_zone,
            a.is_internet_facing = asset.is_internet_facing,
            a.risk_score = asset.risk_score,
            a.business_unit = asset.business_unit
        """
        await neo4j_client.run_write(query, {"assets": assets})
        logger.info(f"Created {len(assets)} asset nodes")

    async def build_vulnerability_nodes(self, vulnerabilities: List[Dict]):
        """Create vulnerability nodes."""
        query = """
        UNWIND $vulns AS v
        MERGE (vuln:Vulnerability {cve_id: v.cve_id})
        SET vuln.cvss_score = v.cvss_score,
            vuln.epss_score = v.epss_score,
            vuln.is_kev = v.is_kev,
            vuln.exploit_probability = v.exploit_probability,
            vuln.attack_vector = v.attack_vector,
            vuln.has_exploit = v.has_exploit,
            vuln.severity = v.severity
        """
        await neo4j_client.run_write(query, {"vulns": vulnerabilities})
        logger.info(f"Created {len(vulnerabilities)} vulnerability nodes")

    async def build_zone_nodes(self, zones: List[str]):
        """Create network zone nodes."""
        query = """
        UNWIND $zones AS zone
        MERGE (z:NetworkZone {name: zone})
        """
        await neo4j_client.run_write(query, {"zones": zones})

    async def build_privilege_nodes(self):
        """Create privilege level nodes."""
        levels = ["system", "admin", "user", "service", "guest"]
        query = """
        UNWIND $levels AS level
        MERGE (p:Privilege {level: level})
        """
        await neo4j_client.run_write(query, {"levels": levels})

    async def build_relationships(self, matches: List[Dict], assets: List[Dict]):
        """Build edges: asset ↔ vulnerability, asset ↔ zone, connectivity."""
        
        # Asset → Vulnerability (AFFECTED_BY)
        vuln_query = """
        UNWIND $matches AS m
        MATCH (a:Asset {asset_id: m.asset_id})
        MATCH (v:Vulnerability {cve_id: m.cve_id})
        MERGE (a)-[r:AFFECTED_BY]->(v)
        SET r.confidence = m.confidence,
            r.software = m.software_name
        """
        if matches:
            await neo4j_client.run_write(vuln_query, {"matches": matches})

        # Asset → NetworkZone (IN_ZONE)
        zone_query = """
        UNWIND $assets AS asset
        MATCH (a:Asset {asset_id: asset.id})
        MATCH (z:NetworkZone {name: asset.network_zone})
        MERGE (a)-[:IN_ZONE]->(z)
        """
        await neo4j_client.run_write(zone_query, {"assets": assets})

        # Zone ↔ Zone (connectivity)
        connectivity = [
            ("external", "dmz", "CONNECTS_TO"),
            ("dmz", "internal", "CONNECTS_TO"),
            ("internal", "restricted", "CONNECTS_TO"),
            ("cloud", "dmz", "CONNECTS_TO"),
            ("cloud", "internal", "CONNECTS_TO"),
        ]
        for src, dst, rel in connectivity:
            q = f"""
            MATCH (z1:NetworkZone {{name: $src}})
            MATCH (z2:NetworkZone {{name: $dst}})
            MERGE (z1)-[:{rel}]->(z2)
            """
            await neo4j_client.run_write(q, {"src": src, "dst": dst})

        # Privilege escalation edges
        priv_edges = [
            ("guest", "user"), ("user", "admin"),
            ("admin", "system"), ("service", "admin"),
        ]
        for low, high in priv_edges:
            q = """
            MATCH (p1:Privilege {level: $low})
            MATCH (p2:Privilege {level: $high})
            MERGE (p1)-[:ESCALATES_TO]->(p2)
            """
            await neo4j_client.run_write(q, {"low": low, "high": high})

        logger.info("Built all graph relationships")

    async def build_full_graph(self, assets: List[Dict], vulnerabilities: List[Dict], matches: List[Dict]):
        """Build the complete attack graph."""
        await self.clear_graph()
        await neo4j_client.ensure_indexes()

        zones = list(set(a.get("network_zone", "internal") for a in assets))
        
        await self.build_zone_nodes(zones)
        await self.build_privilege_nodes()
        await self.build_asset_nodes(assets)
        await self.build_vulnerability_nodes(vulnerabilities)
        await self.build_relationships(matches, assets)

        logger.info("Full attack graph built successfully")
