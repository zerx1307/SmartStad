"""
Automated Pytest Suite for FIFA 2026 Nexus AI Server
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from backend.main import app
from backend.ai_engine import ai_engine

client = TestClient(app)

def test_stadiums_endpoint():
    response = client.get("/api/stadiums")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["stadiums"]) >= 3

def test_stadium_detail_endpoint():
    response = client.get("/api/stadium/metlife")
    assert response.status_code == 200
    data = response.json()
    assert "MetLife Stadium" in data["stadium"]["name"]

def test_fan_chat_multilingual():
    # English test
    resp1 = client.post("/api/fan/chat", json={"query": "Which gate is fastest?", "stadium_id": "metlife"})
    assert resp1.status_code == 200
    assert "status" in resp1.json() and resp1.json()["status"] == "success"
    
    # Spanish test
    resp2 = client.post("/api/fan/chat", json={"query": "Donde puedo comer tacos?", "stadium_id": "metlife"})
    assert resp2.status_code == 200
    assert resp2.json()["data"]["language"] == "es"

def test_ops_incident_triage():
    resp = client.post("/api/ops/incident", json={
        "description": "Gate C turnstile queue overflow into north plaza",
        "stadium_id": "metlife"
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "sop_playbook" in data
    assert "pa_announcements" in data
    assert len(data["sop_playbook"]) >= 3

def test_volunteer_briefing():
    resp = client.post("/api/ops/briefing", json={
        "stadium_id": "metlife",
        "role": "Gate & Accessibility Concierge"
    })
    assert resp.status_code == 200
    assert "briefing" in resp.json()

def test_vision_scanner():
    resp = client.post("/api/vision/parse", data={"image_type": "ticket"})
    assert resp.status_code == 200
    assert "data" in resp.json()
    assert "type" in resp.json()["data"]
