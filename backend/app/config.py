from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ── Database ──
    # SQLite for local dev (no Docker needed); override via DATABASE_URL env var for PostgreSQL
    DATABASE_URL: str = "sqlite+aiosqlite:///./vulnguard.db"
    
    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ── Neo4j ──
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_secret"
    
    # ── Elasticsearch ──
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    
    # ── JWT ──
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    
    # ── API Keys ──
    NVD_API_KEY: Optional[str] = None
    SHODAN_API_KEY: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    
    # ── App ──
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
