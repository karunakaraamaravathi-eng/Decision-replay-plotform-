import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.seed import seed_database

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Milestone 1" in data["milestone"]

def test_wireframe_requirements():
    response = client.get("/api/wireframes/requirements")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Expert Decision Replay Platform"
    assert len(data["outcomes"]) > 0

def test_wireframe_db_schema():
    response = client.get("/api/wireframes/db-schema")
    assert response.status_code == 200
    data = response.json()
    table_names = [t["name"] for t in data["tables"]]
    assert "users" in table_names
    assert "decisions" in table_names
    assert "audit_logs" in table_names

def test_user_login_admin():
    response = client.post("/api/auth/login", json={
        "email": "admin@expert.org",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "Administrator"

def test_user_login_invalid():
    response = client.post("/api/auth/login", json={
        "email": "admin@expert.org",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

import uuid

def test_user_registration():
    random_email = f"newuser_{uuid.uuid4().hex[:6]}@expert.org"
    response = client.post("/api/auth/register", json={
        "email": random_email,
        "password": "password123",
        "full_name": "New Test User",
        "role": "Employee"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == random_email
    assert data["role"] == "Employee"

def test_protected_me_endpoint():
    # Login first
    login_res = client.post("/api/auth/login", json={
        "email": "manager@expert.org",
        "password": "manager123"
    })
    token = login_res.json()["access_token"]

    # Call /me with bearer token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    data = me_res.json()
    assert data["email"] == "manager@expert.org"
    assert data["role"] == "Manager"

def test_admin_update_role():
    # Login as Admin
    login_res = client.post("/api/auth/login", json={
        "email": "admin@expert.org",
        "password": "admin123"
    })
    token = login_res.json()["access_token"]

    # Update employee (user id 4) to Reviewer
    update_res = client.put(
        "/api/users/4/role",
        json={"role": "Reviewer"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["role"] == "Reviewer"
