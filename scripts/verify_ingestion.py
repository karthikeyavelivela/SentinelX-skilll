import requests
import sys

BASE_URL = "http://localhost:8000"

def main():
    # Login
    print("Logging in...")
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "admin", "password": "admin123"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            sys.exit(1)
        
        token_data = resp.json()
        token = token_data["access_token"]
        print(f"Login successful. Token: {token[:20]}...")
    except Exception as e:
        print(f"Login error: {e}")
        sys.exit(1)

    # Trigger Ingestion
    print("\nTriggering NVD Ingestion (1 day)...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/api/cves/ingest/nvd?days_back=1", headers=headers)
    if resp.status_code == 200:
        print("Ingestion triggered successfully:", resp.json())
    else:
        print(f"Ingestion trigger failed: {resp.status_code} {resp.text}")

    # Check CVE list (might be empty initially until Celery runs)
    print("\nChecking CVE list...")
    resp = requests.get(f"{BASE_URL}/api/cves", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Found {data.get('total', 0)} CVEs")
    else:
        print(f"Failed to list CVEs: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    main()
