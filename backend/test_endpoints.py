import sys
from pathlib import Path
from starlette.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.main import app

client = TestClient(app)

def test_api():
    print("=== TESTING FASTAPI ENDPOINTS ===")

    # 1. Health Check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    print(f"[OK] GET /api/health -> {res.json()}")

    # 2. Command: AI Explainer
    res = client.post("/api/command", json={"command": "explain microservices"})
    assert res.status_code == 200
    data = res.json()
    assert data["category"] == "ai_knowledge"
    print(f"[OK] POST /api/command ('explain microservices') -> Category: {data['category']}")

    # 3. Command: Code Gen
    res = client.post("/api/command", json={"command": "generate code for binary search"})
    assert res.status_code == 200
    data = res.json()
    assert data["category"] == "developer_tools"
    print(f"[OK] POST /api/command ('binary search') -> Code language: {data['display']['language']}")

    # 4. Command: Crypto
    res = client.post("/api/command", json={"command": "price of bitcoin"})
    assert res.status_code == 200
    print(f"[OK] POST /api/command ('price of bitcoin') -> Speech: {res.json()['speech'][:60]}...")

    # 5. Telemetry
    res = client.get("/api/telemetry")
    assert res.status_code == 200
    telem = res.json()["display"]["telemetry"]
    print(f"[OK] GET /api/telemetry -> CPU: {telem['cpu_percent']}%, RAM: {telem['ram_percent']}%")

    # 6. Quick Actions
    res = client.get("/api/quick-actions")
    assert res.status_code == 200
    cats = len(res.json()["categories"])
    print(f"[OK] GET /api/quick-actions -> {cats} categories returned")

    # 7. Frontend index.html served at root
    res = client.get("/")
    assert res.status_code == 200
    assert "<title>JARVIS" in res.text
    print(f"[OK] GET / -> Successfully serves frontend/index.html (Length: {len(res.text)} bytes)")

    print("\nALL FASTAPI ENDPOINT TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    test_api()
