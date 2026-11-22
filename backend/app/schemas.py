from pydantic import BaseModel, Field, field_validator
from typing import Literal

class AnalyzeRequest(BaseModel):
    resume_text: str = Field(min_length=10, max_length=50_000)
    job_text: str = Field(min_length=10, max_length=50_000)
    resume_skills: list[str] = Field(default_factory=list)
    job_skills: list[str] = Field(default_factory=list)

class ScoreBreakdown(BaseModel):
    b0_tfidf: float
    b1_semantic: float | None = None
    b2_semantic_skill: float
    skill_overlap: float

class AnalyzeResponse(BaseModel):
    scores: ScoreBreakdown
    shared_skills: list[str]
    not_evidenced_skills: list[str]
    caveat: str = "Similarity is not a hiring probability. Not evidenced means not found in submitted text."

class RankRequest(BaseModel):
    resume_text: str = Field(min_length=10, max_length=50_000)
    model: Literal["B0", "B1", "B2"] = "B2"
    limit: int = Field(default=10, ge=1, le=100)

class RewriteRequest(BaseModel):
    resume_text: str = Field(min_length=10, max_length=50_000)
    job_text: str = Field(min_length=10, max_length=50_000)
    missing_skills: list[str] = Field(default_factory=list)
    mode: Literal["unguided", "gap_guided"] = "gap_guided"

class RewriteResponse(BaseModel):
    available: bool
    draft: str | None = None
    warning: str = "Review every statement. Generated text is not verified for factual accuracy."
