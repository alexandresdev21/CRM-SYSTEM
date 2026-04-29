"""
Testes básicos do CRM.
Execute: python tests/test_api.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
import pytest
from app import create_app, db


@pytest.fixture
def client():
    app = create_app("development")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json["status"] == "ok"


def test_create_and_get_client(client):
    payload = {"name": "Teste Cliente", "email": "teste@email.com", "status": "ativo"}
    r = client.post("/api/clients/", json=payload)
    assert r.status_code == 201
    data = r.json
    assert data["name"] == "Teste Cliente"
    assert data["email"] == "teste@email.com"

    r2 = client.get(f"/api/clients/{data['id']}")
    assert r2.status_code == 200
    assert r2.json["id"] == data["id"]


def test_duplicate_email(client):
    payload = {"name": "A", "email": "dup@email.com"}
    client.post("/api/clients/", json=payload)
    r = client.post("/api/clients/", json=payload)
    assert r.status_code == 409


def test_list_clients_with_filter(client):
    client.post("/api/clients/", json={"name": "Ativo", "email": "ativo@x.com", "status": "ativo"})
    client.post("/api/clients/", json={"name": "Inativo", "email": "inativo@x.com", "status": "inativo"})
    r = client.get("/api/clients/?status=ativo")
    assert r.status_code == 200
    assert all(c["status"] == "ativo" for c in r.json["data"])


def test_create_campaign(client):
    payload = {"name": "Campanha Teste", "channel": "email", "status": "rascunho"}
    r = client.post("/api/campaigns/", json=payload)
    assert r.status_code == 201
    assert r.json["name"] == "Campanha Teste"


def test_client_stats(client):
    client.post("/api/clients/", json={"name": "X", "email": "x@x.com", "status": "ativo"})
    r = client.get("/api/clients/stats")
    assert r.status_code == 200
    assert "total" in r.json


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
