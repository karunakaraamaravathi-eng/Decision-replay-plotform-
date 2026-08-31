import os
import sys
import pytest
import io
from fastapi.testclient import TestClient

# Ensure workspace root is in sys.path when running standalone
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database import Base, engine, SessionLocal
from app.seed import seed_database

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()

def get_auth_header(email="manager@expert.org", password="manager123"):
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_health_check_m2():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Milestone 2" in data["milestone"]

def test_list_decisions_seed():
    response = client.get("/api/decisions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    titles = [d["title"] for d in data]
    assert "Database Engine Selection for Replay Engine" in titles

def test_filter_decisions_by_category():
    response = client.get("/api/decisions?category=Architecture")
    assert response.status_code == 200
    data = response.json()
    assert all(d["category"] == "Architecture" for d in data)

def test_create_decision_with_alternatives():
    headers = get_auth_header("manager@expert.org", "manager123")
    payload = {
        "title": "API Gateway Framework Selection",
        "problem_statement": "Evaluate Kong vs NGINX vs FastAPI Built-in Router for central request routing.",
        "category": "Infrastructure",
        "status": "Draft",
        "rationale": "High throughput routing with low latency overhead.",
        "alternatives": [
            {
                "title": "Kong API Gateway",
                "description": "Enterprise cloud-native API gateway built on NGINX/Lua.",
                "pros": "Rich plugin ecosystem, OAuth2 support.",
                "cons": "Higher memory footprint.",
                "estimated_cost": 200.0,
                "risk_level": "Medium",
                "feasibility_score": 8
            },
            {
                "title": "FastAPI Built-in Router",
                "description": "Use native Python FastAPI routing.",
                "pros": "Zero additional infrastructure overhead.",
                "cons": "Single point of CPU bottleneck.",
                "estimated_cost": 0.0,
                "risk_level": "Low",
                "feasibility_score": 9
            }
        ]
    }
    response = client.post("/api/decisions", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API Gateway Framework Selection"
    assert data["version"] == 1
    assert len(data["alternatives"]) == 2

def test_update_decision_version_bump():
    headers = get_auth_header("admin@expert.org", "admin123")
    # Fetch decision 2
    d2_res = client.get("/api/decisions/2")
    orig_version = d2_res.json()["version"]

    # Update decision 2
    update_payload = {
        "status": "Approved",
        "rationale": "Approved after DevOps infrastructure architecture review.",
        "change_summary": "Promoted decision status from Under Review to Approved."
    }
    put_res = client.put("/api/decisions/2", json=update_payload, headers=headers)
    assert put_res.status_code == 200
    updated = put_res.json()
    assert updated["version"] == orig_version + 1
    assert updated["status"] == "Approved"

    # Verify version history table has snapshot
    v_res = client.get("/api/decisions/2/versions")
    assert v_res.status_code == 200
    versions = v_res.json()
    assert len(versions) >= 2
    latest = versions[0]
    assert latest["version"] == orig_version + 1
    assert latest["status"] == "Approved"

def test_alternative_comparison_matrix():
    response = client.get("/api/decisions/1/alternatives/comparison")
    assert response.status_code == 200
    data = response.json()
    assert data["decision_id"] == 1
    assert data["total_alternatives"] >= 2
    assert "recommended_option" in data
    assert data["recommended_option"] is not None

def test_discussion_comments():
    headers = get_auth_header("employee@expert.org", "emp123")
    comment_payload = {
        "content": "Automated unit test comment: Database indexing should be verified for JSONB columns."
    }
    post_res = client.post("/api/decisions/1/comments", json=comment_payload, headers=headers)
    assert post_res.status_code == 201
    comment_data = post_res.json()
    assert comment_data["content"] == comment_payload["content"]
    assert comment_data["author_name"] is not None

    # Fetch all comments for decision 1
    get_res = client.get("/api/decisions/1/comments")
    assert get_res.status_code == 200
    comments = get_res.json()
    assert any(c["content"] == comment_payload["content"] for c in comments)

def test_file_upload_and_download():
    headers = get_auth_header("manager@expert.org", "manager123")
    file_content = b"Sample Decision Attachment Specification Content\nLine 2 test."
    file_obj = io.BytesIO(file_content)

    upload_res = client.post(
        "/api/decisions/1/upload",
        files={"file": ("test_doc.txt", file_obj, "text/plain")},
        headers=headers
    )
    assert upload_res.status_code == 201
    attachment = upload_res.json()
    assert attachment["filename"] == "test_doc.txt"
    att_id = attachment["id"]

    # Test downloading file
    download_res = client.get(f"/api/attachments/{att_id}/download")
    assert download_res.status_code == 200
    assert download_res.content == file_content

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  RUNNING MILESTONE 2 AUTOMATED TEST SUITE")
    print("=" * 60 + "\n")
    exit_code = pytest.main(["-v", "-s", __file__])
    sys.exit(exit_code)
