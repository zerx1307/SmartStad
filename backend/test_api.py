"""
Automated Test Verification Script for FIFA 2026 Nexus AI Server
"""

import sys
import os

# Add root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_stadiums_endpoint():
    print("Testing /api/stadiums...")
    response = client.get("/api/stadiums")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["stadiums"]) >= 3
    print("[OK] /api/stadiums OK")

def test_stadium_detail_endpoint():
    print("Testing /api/stadium/metlife...")
    response = client.get("/api/stadium/metlife")
    assert response.status_code == 200
    data = response.json()
    assert data["stadium"]["name"] == "MetLife Stadium (New York / New Jersey)"
    print("[OK] /api/stadium/metlife OK")

def test_fan_chat_multilingual():
    print("Testing GenAI Fan Assistant chat endpoint...")
    # Test English
    resp1 = client.post("/api/fan/chat", json={"query": "Which gate is fastest?", "stadium_id": "metlife"})
    assert resp1.status_code == 200
    assert "Live Gate Flow" in resp1.json()["data"]["response"] or "MetLife Stadium" in resp1.json()["data"]["response"]
    
    # Test Spanish
    resp2 = client.post("/api/fan/chat", json={"query": "Donde puedo comer tacos?", "stadium_id": "metlife"})
    assert resp2.status_code == 200
    assert "concessions" in resp2.json()["data"]["category"] or "food" in resp2.json()["data"]["response"].lower()
    print("[OK] Multilingual Fan Assistant OK")

def test_ops_incident_triage():
    print("Testing GenAI Ops Incident Triage & SOP generator...")
    resp = client.post("/api/ops/incident", json={
        "description": "Gate C turnstile queue overflow into north plaza",
        "stadium_id": "metlife"
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "sop_playbook" in data
    assert "pa_announcements" in data
    print("[OK] Ops Incident Triage & SOP Generator OK")

def test_vision_scanner():
    print("Testing GenAI Vision Scanner endpoint...")
    resp = client.post("/api/vision/parse", data={"image_type": "ticket"})
    assert resp.status_code == 200
    assert "Match" in resp.json()["data"]["type"]
    print("[OK] Vision Scanner OK")

if __name__ == "__main__":
    print("--- Running FIFA 2026 Nexus AI Automated Tests ---")
    test_stadiums_endpoint()
    test_stadium_detail_endpoint()
    test_fan_chat_multilingual()
    test_ops_incident_triage()
    test_vision_scanner()
    print("--- ALL AUTOMATED TESTS PASSED SUCCESSFULLY! ---")
