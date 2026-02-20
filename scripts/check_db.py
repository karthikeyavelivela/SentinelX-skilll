import os
from sqlalchemy import create_engine, text

def check_db():
    # Check possible locations
    paths = ["backend/vulnguard.db", "vulnguard.db"]
    
    for p in paths:
        if os.path.exists(p):
            print(f"Checking DB at: {os.path.abspath(p)}")
            try:
                engine = create_engine(f"sqlite:///{p}")
                with engine.connect() as conn:
                    # Check tables
                    tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
                    print(f"Tables: {[t[0] for t in tables]}")
                    
                    if ('cves',) in tables:
                        count = conn.execute(text("SELECT count(*) FROM cves")).scalar()
                        print(f"CVE Count: {count}")
                    else:
                        print("No 'cves' table found.")
            except Exception as e:
                print(f"Error reading {p}: {e}")
            print("-" * 30)
        else:
            print(f"DB not found at: {os.path.abspath(p)}")

if __name__ == "__main__":
    check_db()
