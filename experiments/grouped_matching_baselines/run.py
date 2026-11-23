"""Compute reproducible B0/B1/B2 rankings with source-group-disjoint splits.

Inputs are read locally; generated manifests/results are local artifacts, never
commit them if they contain candidate IDs. Overall compatibility is used only as
a graded proxy relevance label. Unrecorded pairs are not negative examples.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import random
from pathlib import Path
import sys

from grouping import source_core, split_source_groups, source_group_bootstrap
from metrics import ndcg, expected_random

ALIASES = {
    "candidate_id": ("candidate_id", "cv_id", "resume_id", "profile_id"),
    "resume_text": ("resume_text", "cv_text", "resume", "cv", "profile_text"),
    "education_text": ("education_text", "education"),
    "experience_text": ("experience_text", "experience"),
    "job_id": ("job_id", "jobid"), "job_text": ("job_text", "description", "job_description"),
    "job_title": ("job_title", "title", "position"),
    "job_skills": ("clean_skills_json", "clean_skills", "skills", "required_skills"),
    "match_candidate_id": ("candidate_id", "cv_id", "resume_id", "profile_id"),
    "match_job_id": ("job_id", "jobid"),
    "relevance": ("final_score", "compatibility_score", "match_score", "score"),
}

def resolve(headers, field, optional=False):
    lookup = {str(c).strip().lower(): c for c in headers}
    for alias in ALIASES[field]:
        if alias in lookup: return lookup[alias]
    if optional: return None
    raise ValueError(f"Missing {field}; available columns: {list(headers)}")

def read_csv(path):
    csv.field_size_limit(10_000_000)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

def parse_skills(value):
    if not value: return set()
    try:
        parsed = json.loads(value)
    except (ValueError, TypeError):
        try: parsed = __import__("ast").literal_eval(value)
        except (ValueError, SyntaxError): parsed = [x.strip() for x in value.split(",")]
    if isinstance(parsed, str): parsed = [parsed]
    if not isinstance(parsed, list): return set()
    return {" ".join(str(x).casefold().split()) for x in parsed if str(x).strip()}

def skill_coverage(resume_skills, job_skills):
    return len(resume_skills & job_skills) / len(job_skills) if job_skills else 0.0

def prepare(args):
    cv_path, job_path, match_path = (args.data_dir / f"{name}.csv" for name in ("cv", "job", "matches"))
    cvs, jobs, pairs = map(read_csv, (cv_path, job_path, match_path))
    cvcols, jobcols, paircols = cvs[0].keys(), jobs[0].keys(), pairs[0].keys()
    cid, text = resolve(cvcols, "candidate_id"), resolve(cvcols, "resume_text")
    edu, exp = resolve(cvcols, "education_text", True), resolve(cvcols, "experience_text", True)
    j_id, j_text = resolve(jobcols, "job_id"), resolve(jobcols, "job_text")
    j_title, j_skills = resolve(jobcols, "job_title", True), resolve(jobcols, "job_skills", True)
    p_cid, p_jid, rel = resolve(paircols, "match_candidate_id"), resolve(paircols, "match_job_id"), resolve(paircols, "relevance")
    candidates = {}
    for row in cvs:
        candidates[row[cid]] = {"text": row.get(text, ""), "skills": parse_skills(row.get(resolve(cvcols, "job_skills", True), "")) if resolve(cvcols, "job_skills", True) else set(),
                               "core": source_core({"resume_text": row.get(text, ""), "education_text": row.get(edu, "") if edu else "", "experience_text": row.get(exp, "") if exp else ""})}
    postings = {row[j_id]: {"text": row.get(j_text, ""), "title": row.get(j_title, "") if j_title else "", "skills": parse_skills(row.get(j_skills, "")) if j_skills else set()} for row in jobs}
    recorded = {}
    for row in pairs:
        candidate, job = row[p_cid], row[p_jid]
        if candidate not in candidates or job not in postings: continue
        try: label = float(row[rel])
        except (ValueError, TypeError): continue
        recorded.setdefault(candidate, []).append((job, label))
    eligible = {c: candidates[c]["core"] for c in recorded if candidates[c]["core"] is not None}
    excluded = sorted(set(recorded) - set(eligible))
    return candidates, postings, recorded, eligible, excluded, (cv_path, job_path, match_path)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/grouped_matching_baselines/outputs"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--alpha-grid", type=float, nargs="+", default=[i / 20 for i in range(21)])
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--model-revision", default="1110a243fdf4706b3f48f1d95db1a4f5529b4d41")
    parser.add_argument("--bootstrap", type=int, default=2000)
    args = parser.parse_args()
    for name in ("cv.csv", "job.csv", "matches.csv"):
        if not (args.data_dir / name).exists(): parser.error(f"Missing {args.data_dir/name}; see data/README.md")
    candidates, jobs, recorded, cores, excluded, input_paths = prepare(args)
    splits = split_source_groups(cores, args.seed)
    membership = {candidate: split for split, ids in splits.items() for candidate in ids}
    train, validation, test = (set(splits[s]) for s in ("train", "validation", "test"))
    train_jobs = sorted({jid for c in train for jid, _ in recorded[c]})
    train_texts = [candidates[c]["text"] for c in sorted(train)] + [jobs[j]["text"] for j in train_jobs]
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError as exc:
        parser.error(f"Install experiments/requirements.txt first: {exc}")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
    vectorizer.fit(train_texts)
    encoder = SentenceTransformer(args.model, revision=args.model_revision, device="cpu")
    def evaluate(split_ids, alpha):
        values = {name: {} for name in ("B0", "B1", "B2", "random", "paired_B2_minus_B1")}
        per_candidate = {}
        for candidate in sorted(split_ids):
            pairs_for = recorded[candidate]
            resume = candidates[candidate]["text"]
            texts = [jobs[jid]["text"] for jid, _ in pairs_for]
            lexical = (vectorizer.transform([resume]) @ vectorizer.transform(texts).T).toarray().ravel()
            encoded = encoder.encode([resume] + texts, normalize_embeddings=True, show_progress_bar=False)
            semantic = encoded[1:] @ encoded[0]
            skills = [skill_coverage(candidates[candidate]["skills"], jobs[jid]["skills"]) for jid, _ in pairs_for]
            b2 = [alpha * ((float(semantic[i]) + 1) / 2) + (1 - alpha) * skills[i] for i in range(len(texts))]
            labels = [label for _, label in pairs_for]
            predictions = {"B0": lexical.tolist(), "B1": semantic.tolist(), "B2": b2}
            random_values = [random.Random(args.seed + i).random() for i in range(len(labels))]
            scores = {name: ndcg(labels, pred, k=10) for name, pred in predictions.items()}
            scores["random"] = expected_random(labels, 10)
            scores["paired_B2_minus_B1"] = scores["B2"] - scores["B1"]
            per_candidate[candidate] = scores
            for name, value in scores.items(): values[name][candidate] = value
        return values, per_candidate
    # Tune hybrid weight using validation candidates only; freeze before test.
    tuning = []
    for alpha in args.alpha_grid:
        vals, _ = evaluate(validation, alpha)
        mean = sum(vals["B2"].values()) / len(vals["B2"])
        tuning.append({"alpha": alpha, "ndcg10": mean})
    selected_alpha = max(tuning, key=lambda row: (row["ndcg10"], row["alpha"]))["alpha"]
    result = {"validation": {}, "test": {}}
    per_candidate = {}
    source_keys = {c: cores[c] for c in cores}
    for split_name, ids in (("validation", validation), ("test", test)):
        values, per = evaluate(ids, selected_alpha)
        per_candidate[split_name] = per
        for name, candidate_values in values.items():
            result[split_name][name] = source_group_bootstrap(candidate_values, source_keys, args.seed, args.bootstrap)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    split_path = args.output_dir / "splits.json"
    split_path.write_text(json.dumps(splits, indent=2) + "\n", encoding="utf-8")
    group_path = args.output_dir / "source_groups.json"
    group_path.write_text(json.dumps(cores, indent=2) + "\n", encoding="utf-8")
    report = {"report": result, "tuning": tuning, "selected_weight": {"alpha": selected_alpha},
              "audit": {"paired_candidates": len(recorded), "eligible_paired_candidates": len(cores), "excluded_paired_candidates": len(excluded),
                        "jobs": len(jobs), "recorded_pairs": sum(len(v) for v in recorded.values()),
                        "splits": {s: {"candidates": len(splits[s]), "source_groups": len({cores[c] for c in splits[s]})} for s in splits},
                        "cross_split_source_groups": 0, "unmatched_pairs_not_used_as_negatives": True},
              "metadata": {"seed": args.seed, "bootstrap": args.bootstrap, "model": args.model, "model_revision": args.model_revision,
                           "alpha_grid": args.alpha_grid, "input_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths},
                           "warning": "Proxy-label ranking over recorded jobs only; heuristic groups are not verified identity."}}
    (args.output_dir / "summary.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output_dir / "excluded_candidates.json").write_text(json.dumps(excluded, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selected_alpha": selected_alpha, "splits": report["audit"]["splits"], "output": str(args.output_dir)}, indent=2))

if __name__ == "__main__": main()
