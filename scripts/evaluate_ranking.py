"""Evaluate B0/B1/B2 resume-to-job ranking on recorded candidate/job pairs.

The dataset's overall compatibility score is used only as graded proxy relevance.
Component subscores are never used as features; unrecorded pairs are not negatives.
Candidate IDs are split as groups. Metrics are computed only over each test
candidate's recorded job pool. This script reports proxy-benchmark agreement, not
hiring quality.

Example:
  python scripts/evaluate_ranking.py --cv data/cv.csv --jobs data/job.csv \
    --matches data/matches.csv --output reports/ranking_metrics.csv
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILL_VOCAB = {
    "python", "sql", "java", "javascript", "typescript", "machine learning",
    "deep learning", "data analysis", "data pipelines", "aws", "azure", "gcp",
    "docker", "kubernetes", "communication", "project management", "excel",
    "power bi", "tableau", "salesforce", "leadership", "customer service",
}
ALIASES = {
    "candidate_id": ["candidate_id", "cv_id", "resume_id", "profile_id", "id"],
    "resume": ["resume_text", "cv_text", "resume", "cv", "profile_text", "text", "description"],
    "resume_skills": ["clean_skills", "skills", "candidate_skills"],
    "job_id": ["job_id", "id", "jobid"],
    "title": ["title", "job_title", "position", "role"],
    "job_text": ["job_text", "job_description", "description", "text"],
    "job_skills": ["clean_skills", "skills", "required_skills"],
    "match_candidate_id": ["candidate_id", "cv_id", "resume_id", "profile_id"],
    "match_job_id": ["job_id", "jobid"],
    "relevance": ["final_score", "compatibility_score", "match_score", "score", "relevance"],
}


def column(frame: pd.DataFrame, field: str, required: bool = True) -> str | None:
    lookup = {str(c).strip().lower(): c for c in frame.columns}
    for alias in ALIASES[field]:
        if alias in lookup:
            return lookup[alias]
    if required:
        raise ValueError(f"Could not find '{field}'. Available columns: {list(frame.columns)}")
    return None


def clean_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def parse_skills(value: Any, text: str) -> set[str]:
    supplied: set[str] = set()
    if value is not None and not pd.isna(value):
        raw = str(value).strip()
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                supplied.update(str(x).strip().lower() for x in parsed if str(x).strip())
            elif isinstance(parsed, str):
                supplied.update(x.strip().lower() for x in re.split(r"[,;|]", parsed) if x.strip())
        except (json.JSONDecodeError, TypeError):
            supplied.update(x.strip().lower() for x in re.split(r"[,;|]", raw) if x.strip())
    low = text.lower()
    supplied.update(skill for skill in SKILL_VOCAB if re.search(r"(?<!\w)" + re.escape(skill) + r"(?!\w)", low))
    return supplied


def jaccard(a: set[str], b: set[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def ndcg(relevances: list[float], order: list[int], k: int) -> float:
    def dcg(indices: list[int]) -> float:
        return sum((2 ** max(0.0, relevances[i]) - 1) / math.log2(rank + 2) for rank, i in enumerate(indices[:k]))
    ideal_order = sorted(range(len(relevances)), key=lambda i: relevances[i], reverse=True)
    ideal = dcg(ideal_order)
    return dcg(order) / ideal if ideal > 0 else 0.0


def split_ids(ids: list[str], test_fraction: float, seed: int) -> set[str]:
    shuffled = sorted(set(ids))
    random.Random(seed).shuffle(shuffled)
    count = max(1, math.ceil(len(shuffled) * test_fraction)) if len(shuffled) > 1 else 1
    return set(shuffled[:count])


def evaluate_candidate(resume: str, resume_skills: set[str], job_rows: list[dict], alpha: float, semantic_model=None) -> dict[str, float]:
    job_texts = [f"{r['title']}\n{r['job_text']}".strip() for r in job_rows]
    documents = [resume] + job_texts
    try:
        matrix = TfidfVectorizer(ngram_range=(1, 2), stop_words="english").fit_transform(documents)
        lexical = cosine_similarity(matrix[0:1], matrix[1:]).ravel().tolist()
    except ValueError:
        lexical = [0.0] * len(job_rows)
    semantic: list[float] | None = None
    if semantic_model is not None:
        vectors = semantic_model.encode(documents, normalize_embeddings=True, show_progress_bar=False)
        semantic = (vectors[1:] @ vectors[0]).tolist()
    skills = [jaccard(resume_skills, r["skills"]) for r in job_rows]
    base = semantic if semantic is not None else lexical
    return {
        "B0": lexical,
        "B1": semantic if semantic is not None else lexical,
        "B2": [(1 - alpha) * base[i] + alpha * skills[i] for i in range(len(job_rows))],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cv", type=Path, default=Path("data/cv.csv"))
    parser.add_argument("--jobs", type=Path, default=Path("data/job.csv"))
    parser.add_argument("--matches", type=Path, default=Path("data/matches.csv"))
    parser.add_argument("--output", type=Path, default=Path("reports/ranking_metrics.csv"))
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skill-weight", type=float, default=0.25, help="B2 alpha; set using validation data before final test reporting")
    parser.add_argument("--sentence-transformer", default=None, help="Optional model name; requires sentence-transformers")
    args = parser.parse_args()
    if not 0 < args.test_fraction < 1:
        parser.error("--test-fraction must be between 0 and 1")
    if not 0 <= args.skill_weight <= 1:
        parser.error("--skill-weight must be between 0 and 1")
    for path in (args.cv, args.jobs, args.matches):
        if not path.exists():
            parser.error(f"Dataset file not found: {path}")

    cvs, jobs, matches = (pd.read_csv(p).fillna("") for p in (args.cv, args.jobs, args.matches))
    cv_id, resume_col = column(cvs, "candidate_id"), column(cvs, "resume")
    cv_skills_col = column(cvs, "resume_skills", required=False)
    job_id_col, title_col, job_text_col = column(jobs, "job_id"), column(jobs, "title", required=False), column(jobs, "job_text")
    job_skills_col = column(jobs, "job_skills", required=False)
    match_cv_col, match_job_col, relevance_col = column(matches, "match_candidate_id"), column(matches, "match_job_id"), column(matches, "relevance")

    cv_map = {}
    for _, row in cvs.iterrows():
        key = clean_text(row[cv_id])
        text = clean_text(row[resume_col])
        raw_skills = row[cv_skills_col] if cv_skills_col else None
        cv_map[key] = (text, parse_skills(raw_skills, text))
    job_map = {}
    for _, row in jobs.iterrows():
        key = clean_text(row[job_id_col])
        title = clean_text(row[title_col]) if title_col else ""
        text = clean_text(row[job_text_col])
        raw_skills = row[job_skills_col] if job_skills_col else None
        job_map[key] = {"title": title, "job_text": text, "skills": parse_skills(raw_skills, f"{title}\n{text}")}

    records = []
    for _, row in matches.iterrows():
        cid, jid = clean_text(row[match_cv_col]), clean_text(row[match_job_col])
        if cid not in cv_map or jid not in job_map:
            continue
        try:
            relevance = float(row[relevance_col])
        except (TypeError, ValueError):
            continue
        records.append((cid, jid, relevance))
    if not records:
        parser.error("No match rows could be joined to CV and job tables; check ID columns and schema.")

    test_ids = split_ids([r[0] for r in records], args.test_fraction, args.seed)
    semantic_model = None
    if args.sentence_transformer:
        try:
            from sentence_transformers import SentenceTransformer
            semantic_model = SentenceTransformer(args.sentence_transformer)
        except ImportError:
            parser.error("Install sentence-transformers to use --sentence-transformer")

    by_candidate: dict[str, list[tuple[str, float]]] = {}
    for cid, jid, rel in records:
        if cid in test_ids:
            by_candidate.setdefault(cid, []).append((jid, rel))
    metric_values: dict[str, list[float]] = {f"{model}_ndcg@{k}": [] for model in ("B0", "B1", "B2") for k in (5, 10)}
    for cid, pairs in by_candidate.items():
        resume, resume_skills = cv_map[cid]
        job_rows = [job_map[jid] for jid, _ in pairs]
        rels = [rel for _, rel in pairs]
        predictions = evaluate_candidate(resume, resume_skills, job_rows, args.skill_weight, semantic_model)
        for model, scores in predictions.items():
            order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
            for k in (5, 10):
                metric_values[f"{model}_ndcg@{k}"].append(ndcg(rels, order, k))
    summary = {key: (sum(values) / len(values) if values else 0.0) for key, values in metric_values.items()}
    summary.update({"test_candidates": len(by_candidate), "test_recorded_pairs": sum(map(len, by_candidate.values())), "seed": args.seed, "skill_weight": args.skill_weight, "semantic_model": args.sentence_transformer or "disabled (B1 fallback is lexical; not a Sentence-BERT result)"})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([summary]).to_csv(args.output, index=False)
    print(pd.DataFrame([summary]).to_string(index=False))
    print(f"\nSaved metrics to {args.output}")
    print("Interpretation: NDCG measures agreement with the dataset proxy labels over recorded pairs only; it is not hiring performance.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
