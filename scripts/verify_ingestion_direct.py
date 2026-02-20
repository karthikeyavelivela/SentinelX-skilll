import sys
import os
import asyncio
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.ingestion.tasks import _ingest_nvd
from app.database import init_db

# Import all models to ensure they are registered with Base.metadata before init_db
import app.auth.models
import app.ingestion.models
import app.assets.models
import app.matching.models
import app.remediation.models

logging.basicConfig(level=logging.INFO)

async def main():
    print("Initializing DB (creating tables)...")
    await init_db()
    
    # We will run this script from project root, so logical path to db is backend/vulnguard.db?
    # Config says "sqlite+aiosqlite:///./vulnguard.db".
    # If we run from root, it looks in root. Backend runs in backend dir.
    # We should run this script from backend dir context.
    
    print("Triggering NVD Ingestion (1 day) directly...")
    try:
        result = await _ingest_nvd(days_back=1)
        print("Ingestion Result:", result)
        print("Ingestion Result:", result)
    except Exception as e:
        print(f"Ingestion failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Change cwd to backend so DB path matches
    os.chdir(os.path.join(os.path.dirname(__file__), "..", "backend"))
    asyncio.run(main())
