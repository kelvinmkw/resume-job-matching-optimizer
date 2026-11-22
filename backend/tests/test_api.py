import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_analyze_returns_explainable_signals():
    response = client.post("/api/analyze", json={"resume_text": "Python developer with SQL data pipelines and cloud experience.", "job_text": "Python role requiring SQL and AWS cloud skills.", "resume_skills": ["Python", "SQL", "data pipelines"], "job_skills": ["Python", "SQL", "AWS"]})
    assert response.status_code == 200
    result = response.json()
    assert "b0_tfidf" in result["scores"]
    assert "python" in result["shared_skills"]
    assert "aws" in result["not_evidenced_skills"]

def test_invalid_short_text_is_rejected():
    response = client.post("/api/analyze", json={"resume_text": "short", "job_text": "also short"})
    assert response.status_code == 422
