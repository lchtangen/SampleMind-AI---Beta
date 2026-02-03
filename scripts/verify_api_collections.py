import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from fastapi.testclient import TestClient
    from samplemind.interfaces.api.main import app
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure dependencies are installed (fastapi, httpx)")
    sys.exit(1)

def test_collections_api():
    print("Testing Collections API via TestClient...")
    client = TestClient(app)

    # 1. List Collections
    print("\n[1] GET /api/v1/collections/")
    response = client.get("/api/v1/collections/")
    assert response.status_code == 200
    data = response.json()
    print(f"    Found {len(data)} collections")
    assert len(data) >= 2 # We seeded 2 mocks

    # 2. Create Collection
    print("\n[2] POST /api/v1/collections/")
    new_col = {
        "name": "Integration Test Collection",
        "description": "Created by verify script",
        "is_public": False,
        "tags": ["test", "api"]
    }
    response = client.post("/api/v1/collections/", json=new_col)
    assert response.status_code == 200
    created = response.json()
    print(f"    Created ID: {created['id']}")
    assert created["name"] == "Integration Test Collection"
    test_id = created["id"]

    # 3. Get Details
    print(f"\n[3] GET /api/v1/collections/{test_id}")
    response = client.get(f"/api/v1/collections/{test_id}")
    assert response.status_code == 200
    assert response.json()["id"] == test_id

    # 4. Get Items (expect empty for new)
    print(f"\n[4] GET /api/v1/collections/{test_id}/items")
    response = client.get(f"/api/v1/collections/{test_id}/items")
    assert response.status_code == 200 # Should return empty list, not 404 (unless logic logic specifically throws 404 for empty? No logic check existence first)
    # Actually my logic checks existence first, then returns items list.
    assert isinstance(response.json(), list)

    # 5. Delete
    print(f"\n[5] DELETE /api/v1/collections/{test_id}")
    response = client.delete(f"/api/v1/collections/{test_id}")
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f"/api/v1/collections/{test_id}")
    assert response.status_code == 404
    print("    Deletion verified")

    print("\n✅ API Collections Verification Passed!")

if __name__ == "__main__":
    test_collections_api()
