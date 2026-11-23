from pathlib import Path
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app
from app.services.dataset import load_jobs
from app.services.matcher import Matcher

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

def test_pair_and_batch_lexical_scores_use_same_vectorizer_logic():
    matcher = Matcher()
    resume = "Python data engineer with SQL experience"
    jobs = ["Python engineer using SQL", "Accountant using Excel"]
    batch = matcher._lexical_scores(resume, jobs)
    assert len(batch) == 2
    assert batch[0] > batch[1]

def test_job_dataset_reads_json_skill_column(tmp_path, monkeypatch):
    import app.services.dataset as dataset_module
    class TestSettings:
        data_dir = str(tmp_path)
    monkeypatch.setattr(dataset_module, "get_settings", lambda: TestSettings())
    pd.DataFrame([{"job_id": 17, "job_title": "Engineer", "job_text": "Python role", "clean_skills_json": '["Python", "SQL"]'}]).to_csv(tmp_path / "job.csv", index=False)
    loaded = load_jobs()
    assert loaded.iloc[0]["job_id"] == "17"
    assert loaded.iloc[0]["skills"] == ["Python", "SQL"]
