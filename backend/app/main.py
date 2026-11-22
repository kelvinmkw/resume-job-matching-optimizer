from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.schemas import AnalyzeRequest, AnalyzeResponse, RankRequest, RewriteRequest, RewriteResponse
from app.services.skills import find_skills, jaccard
from app.services.matcher import get_matcher
from app.services.dataset import load_jobs, DatasetUnavailable
from app.services.rewriter import rewrite_resume

cfg = get_settings()
app = FastAPI(title=cfg.app_name, version="0.1.0", description="Transparent resume–job text alignment prototype")
app.add_middleware(CORSMiddleware, allow_origins=cfg.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"status": "ok", "semantic_enabled": cfg.matcher_use_sentence_transformers, "rewrite_enabled": cfg.ollama_enabled}

@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    resume_skills = find_skills(request.resume_text, request.resume_skills)
    job_skills = find_skills(request.job_text, request.job_skills)
    scores = get_matcher().score(request.resume_text, request.job_text, resume_skills, job_skills)
    return AnalyzeResponse(scores=scores, shared_skills=sorted(resume_skills & job_skills), not_evidenced_skills=sorted(job_skills - resume_skills))

@app.post("/api/rank")
def rank(request: RankRequest):
    try:
        jobs = load_jobs()
    except DatasetUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    matcher = get_matcher()
    rows = []
    resume_skills = find_skills(request.resume_text)
    for row in jobs.to_dict("records"):
        text = f"{row['title']}\n{row['text']}"
        job_skills = find_skills(text, [s.strip() for s in str(row['skills']).split(",") if s.strip()])
        score = matcher.score(request.resume_text, text, resume_skills, job_skills)
        key = {"B0": "b0_tfidf", "B1": "b1_semantic", "B2": "b2_semantic_skill"}[request.model]
        value = score[key]
        if value is None: value = score["b0_tfidf"]
        rows.append({"job_id": str(row["job_id"]), "title": str(row["title"]), "score": value, "not_evidenced_skills": sorted(job_skills - resume_skills)})
    rows.sort(key=lambda x: x["score"], reverse=True)
    return {"model": request.model, "results": rows[:request.limit], "caveat": "Similarity ranking over loaded jobs only; not a hiring recommendation."}

@app.post("/api/rewrite", response_model=RewriteResponse)
async def rewrite(request: RewriteRequest):
    try:
        draft = await rewrite_resume(request.resume_text, request.job_text, request.missing_skills, request.mode == "gap_guided")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Local rewrite provider failed: {type(exc).__name__}")
    return RewriteResponse(available=draft is not None, draft=draft)
