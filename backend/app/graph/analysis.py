import logging
from typing import List, Dict, Optional
from app.graph.neo4j_client import neo4j_client

logger = logging.getLogger("vulnguard.graph.analysis")


class AttackPathAnalyzer:
    """Analyze attack paths in the graph."""

    async def shortest_path_to_asset(self, source_id: int, target_id: int) -> Dict:
        """Find shortest attack path between two assets."""
        query = """
        MATCH path = shortestPath(
            (source:Asset {asset_id: $source_id})-[*..10]-(target:Asset {asset_id: $target_id})
        )
        RETURN [node in nodes(path) | 
            CASE 
                WHEN node:Asset THEN {type: 'asset', id: node.asset_id, hostname: node.hostname, criticality: node.criticality}
                WHEN node:Vulnerability THEN {type: 'vulnerability', id: node.cve_id, cvss: node.cvss_score}
                WHEN node:NetworkZone THEN {type: 'zone', name: node.name}
                WHEN node:Privilege THEN {type: 'privilege', level: node.level}
                ELSE {type: 'unknown'}
            END
        ] AS path_nodes,
        length(path) AS path_length
        """
        results = await neo4j_client.run_query(query, {
            "source_id": source_id, "target_id": target_id
        })
        
        if results:
            return {
                "path": results[0]["path_nodes"],
                "length": results[0]["path_length"],
                "risk_score": self._calculate_path_risk(results[0]["path_nodes"]),
            }
        return {"path": [], "length": -1, "risk_score": 0}

    async def lateral_movement_paths(self, asset_id: int, max_depth: int = 5) -> List[Dict]:
        """Find all lateral movement paths from an asset."""
        query = """
        MATCH (source:Asset {asset_id: $asset_id})
        MATCH path = (source)-[:IN_ZONE]->(:NetworkZone)-[:CONNECTS_TO]->(:NetworkZone)<-[:IN_ZONE]-(target:Asset)
        WHERE source <> target
        RETURN target.asset_id AS target_id,
               target.hostname AS target_hostname,
               target.criticality AS target_criticality,
               target.risk_score AS target_risk,
               length(path) AS hops
        ORDER BY target.criticality DESC, target.risk_score DESC
        LIMIT 20
        """
        return await neo4j_client.run_query(query, {"asset_id": asset_id})

    async def blast_radius(self, cve_id: str) -> Dict:
        """Estimate the blast radius if a CVE is exploited."""
        query = """
        MATCH (v:Vulnerability {cve_id: $cve_id})<-[:AFFECTED_BY]-(a:Asset)
        OPTIONAL MATCH (a)-[:IN_ZONE]->(z:NetworkZone)-[:CONNECTS_TO*0..3]->(z2:NetworkZone)<-[:IN_ZONE]-(reachable:Asset)
        WHERE reachable <> a
        WITH v, a, collect(DISTINCT reachable) AS reachable_assets
        RETURN v.cve_id AS cve_id,
               v.cvss_score AS cvss_score,
               count(DISTINCT a) AS directly_affected,
               size(reachable_assets) AS indirectly_reachable,
               collect(DISTINCT a.criticality) AS affected_criticalities,
               collect(DISTINCT a.business_unit) AS affected_units
        """
        results = await neo4j_client.run_query(query, {"cve_id": cve_id})
        
        if results:
            r = results[0]
            return {
                "cve_id": cve_id,
                "directly_affected_assets": r.get("directly_affected", 0),
                "indirectly_reachable_assets": r.get("indirectly_reachable", 0),
                "total_blast_radius": r.get("directly_affected", 0) + r.get("indirectly_reachable", 0),
                "affected_criticalities": r.get("affected_criticalities", []),
                "affected_business_units": r.get("affected_units", []),
                "severity": self._blast_severity(
                    r.get("directly_affected", 0) + r.get("indirectly_reachable", 0)
                ),
            }
        return {"cve_id": cve_id, "total_blast_radius": 0, "severity": "none"}

    async def risk_propagation(self) -> List[Dict]:
        """Calculate risk propagation scores across the graph."""
        query = """
        MATCH (a:Asset)-[:AFFECTED_BY]->(v:Vulnerability)
        WITH a, count(v) AS vuln_count, avg(v.cvss_score) AS avg_cvss, max(v.exploit_probability) AS max_prob
        OPTIONAL MATCH (a)-[:IN_ZONE]->(z:NetworkZone)-[:CONNECTS_TO*0..2]->(:NetworkZone)<-[:IN_ZONE]-(neighbor:Asset)
        WHERE neighbor <> a
        WITH a, vuln_count, avg_cvss, max_prob, count(DISTINCT neighbor) AS reachable_count
        RETURN a.asset_id AS asset_id,
               a.hostname AS hostname,
               a.criticality AS criticality,
               vuln_count,
               round(avg_cvss * 100) / 100 AS avg_cvss,
               round(max_prob * 100) / 100 AS max_exploit_prob,
               reachable_count,
               round((vuln_count * avg_cvss * max_prob * (1 + reachable_count * 0.1)) * 100) / 100 AS propagation_score
        ORDER BY propagation_score DESC
        LIMIT 50
        """
        return await neo4j_client.run_query(query)

    async def get_full_graph_data(self) -> Dict:
        """Get all nodes and edges for visualization."""
        nodes_query = """
        MATCH (n)
        RETURN id(n) AS id,
               labels(n)[0] AS type,
               properties(n) AS properties
        """
        edges_query = """
        MATCH (a)-[r]->(b)
        RETURN id(a) AS source,
               id(b) AS target,
               type(r) AS relationship,
               properties(r) AS properties
        """
        nodes = await neo4j_client.run_query(nodes_query)
        edges = await neo4j_client.run_query(edges_query)
        
        return {"nodes": nodes, "edges": edges}

    @staticmethod
    def _calculate_path_risk(path_nodes: list) -> float:
        risk = 0.0
        for node in path_nodes:
            if node.get("type") == "vulnerability":
                risk += node.get("cvss", 0) / 10
            elif node.get("type") == "asset":
                crit_map = {"critical": 1.0, "high": 0.75, "medium": 0.5, "low": 0.25}
                risk += crit_map.get(node.get("criticality", ""), 0.25)
        return round(min(risk / max(len(path_nodes), 1), 10.0), 2)

    @staticmethod
    def _blast_severity(total: int) -> str:
        if total >= 50:
            return "catastrophic"
        elif total >= 20:
            return "critical"
        elif total >= 10:
            return "high"
        elif total >= 5:
            return "medium"
        elif total >= 1:
            return "low"
        return "none"
