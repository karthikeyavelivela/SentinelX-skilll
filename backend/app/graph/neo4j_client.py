import logging
from typing import Optional
from neo4j import AsyncGraphDatabase
from app.config import settings

logger = logging.getLogger("vulnguard.graph.neo4j")


class Neo4jClient:
    """Async Neo4j driver wrapper."""

    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self._driver = None

    async def connect(self):
        if not self._driver:
            self._driver = AsyncGraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )
            logger.info("Connected to Neo4j")

    async def close(self):
        if self._driver:
            await self._driver.close()
            self._driver = None

    async def run_query(self, query: str, params: dict = None) -> list:
        try:
            await self.connect()
            async with self._driver.session() as session:
                result = await session.run(query, params or {})
                # result is an AsyncResult, we need to iterate over it properly
                records = []
                async for record in result:
                    records.append(record.data())
                return records
        except Exception as e:
            logger.error(f"Neo4j query failed (Service likely unavailable): {e}")
            return []

    async def run_write(self, query: str, params: dict = None):
        try:
            await self.connect()
            async with self._driver.session() as session:
                await session.run(query, params or {})
        except Exception as e:
            logger.error(f"Neo4j write failed: {e}")

    async def ensure_indexes(self):
        """Create indexes for performance."""
        await self.connect()
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (a:Asset) ON (a.asset_id)",
            "CREATE INDEX IF NOT EXISTS FOR (v:Vulnerability) ON (v.cve_id)",
            "CREATE INDEX IF NOT EXISTS FOR (z:NetworkZone) ON (z.name)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Privilege) ON (p.level)",
        ]
        for idx in indexes:
            try:
                await self.run_write(idx)
            except Exception as e:
                logger.warning(f"Index creation skipped: {e}")


neo4j_client = Neo4jClient()
