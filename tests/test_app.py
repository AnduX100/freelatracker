import os
import sys
from pathlib import Path
from typing import Dict

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Configurar entorno antes de importar la app
os.environ["FREELATRACKER_SECRET_KEY"] = "tests_secret_key_with_32_chars_minimum!"
os.environ["FREELATRACKER_DATABASE_URL"] = "sqlite:///./freelatracker_test.db"

from app.database import Base, SessionLocal, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.routers import auth as auth_router  # noqa: E402


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    auth_router._login_attempts.clear()


@pytest.fixture(autouse=True)
def reset_rate_limits():
    auth_router._login_attempts.clear()
    yield
    auth_router._login_attempts.clear()


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def _register_user(client: TestClient, email: str = "user@example.com", password: str = "Str0ng!Pass123@"):
    return client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )


def _login(client: TestClient, email: str, password: str) -> Dict:
    res = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert res.status_code == 200, res.text
    return res.json()


def test_password_policy_rejects_weak_password(client: TestClient):
    res = _register_user(client, email="weak@example.com", password="onlyletters")
    assert res.status_code == 422


def test_register_login_and_crud_proposals(client: TestClient):
    email = "proposals@example.com"
    password = "Strong!Pass123"

    res = _register_user(client, email=email, password=password)
    assert res.status_code == 200

    token = _login(client, email, password)["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Crear propuesta
    proposal_body = {
        "client_name": "Cliente 1",
        "platform": "Workana",
        "project_title": "Proyecto A",
        "project_link": "https://example.com/project",
        "amount": 1000,
        "currency": "USD",
        "status": "Enviada",
        "notes": "Primer intento",
    }
    create_res = client.post("/proposals/", json=proposal_body, headers=headers)
    assert create_res.status_code == 200, create_res.text
    proposal_id = create_res.json()["id"]

    # Listar propuestas
    list_res = client.get("/proposals/", headers=headers)
    assert list_res.status_code == 200
    proposals = list_res.json()
    assert len(proposals) == 1
    assert proposals[0]["id"] == proposal_id

    # Actualizar estado rápido
    update_res = client.put(f"/proposals/{proposal_id}", json={"status": "Aceptada"}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "Aceptada"


def test_stats_basic_aggregation(client: TestClient):
    email = "stats@example.com"
    password = "Strong!Pass123"
    _register_user(client, email=email, password=password)
    token = _login(client, email, password)["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payloads = [
        {"client_name": "A", "platform": "Workana", "project_title": "P1", "amount": 10, "currency": "USD", "status": "Aceptada"},
        {"client_name": "B", "platform": "Upwork", "project_title": "P2", "amount": 20, "currency": "USD", "status": "Rechazada"},
        {"client_name": "C", "platform": "Freelancer", "project_title": "P3", "amount": 30, "currency": "USD", "status": "Enviada"},
    ]

    for body in payloads:
        body.setdefault("project_link", None)
        body.setdefault("notes", None)
        res = client.post("/proposals/", json=body, headers=headers)
        assert res.status_code == 200, res.text

    stats_res = client.get("/proposals/stats/basic", headers=headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()

    assert stats["total"] == 3
    assert stats["accepted"] == 1
    assert stats["rejected"] == 1
    assert stats["pending"] == 1
    assert stats["conversion_percent"] == 33.33


def test_logout_revokes_token(client: TestClient):
    email = "logout@example.com"
    password = "Strong!Pass123"
    _register_user(client, email=email, password=password)
    token = _login(client, email, password)["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/auth/logout", headers=headers)
    assert res.status_code == 204, res.text

    # Token should be rejected after logout
    res_after = client.get("/proposals/", headers=headers)
    assert res_after.status_code == 401


def test_login_rate_limit_blocks_after_threshold(client: TestClient):
    email = "ratelimit@example.com"
    password = "Strong!Pass123"
    _register_user(client, email=email, password=password)

    for _ in range(10):
        res = client.post(
            "/auth/login",
            data={"username": email, "password": "bad_password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert res.status_code == 401

    blocked = client.post(
        "/auth/login",
        data={"username": email, "password": "bad_password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert blocked.status_code == 429
