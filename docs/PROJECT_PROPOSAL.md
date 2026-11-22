# Project Proposal: Resume–Job Matching with Semantic Representations, Skill Features, and Constrained LLM Optimization

**Course:** COMP7607: Natural Language Processing  
**Contributors:** Chan Hong Wing (3036656350), Ma Kwan Wei (3036656049), Justin Lau (3036656817), Tsang Shuk Kuen (3036659819)

## 1. Executive summary

This project develops a transparent prototype that helps a job seeker understand how their resume text aligns with one job description and supports reproducible ranking experiments over a dataset of recorded resume–job pairs. It combines lexical similarity, sentence-level semantic similarity, and explicit skill overlap; explains detected gaps as *not evidenced in the submitted text*; and can optionally request a constrained local-LLM rewrite for human review.

The work is about explaining textual alignment, not reproducing a commercial Applicant Tracking System (ATS), making hiring decisions, or claiming that a higher score leads to better employment outcomes. The dataset's compatibility score is a proxy benchmark and must not be interpreted as a human judgment.

## 2. Motivation and objective

High-volume recruitment systems can provide candidates little actionable feedback. A single opaque match percentage fails to distinguish lexical mismatch, semantic mismatch, and missing explicit evidence. Generative rewriting creates another risk: unsupported employers, qualifications, dates, skills, or metrics may be introduced.

Our objective is to build a multi-stage pipeline that: (1) accepts resume and job-description text; (2) extracts lexical, semantic, and skill signals; (3) reports interpretable compatibility scores and evidence; (4) identifies skills found in the job text but not evidenced in the resume; and (5) optionally proposes a conservative, auditable rewrite. In parallel, a dataset workflow compares ranking behavior on recorded pairs.

## 3. Research questions

1. How effectively do lexical, semantic, and skill-aware representations rank relevant jobs for a candidate?
2. What incremental value does explicit skill overlap add beyond semantic embeddings?
3. Can constrained LLM rewriting improve text-alignment scores while maintaining factual integrity?
4. What failure modes remain, including synonyms, sparse resumes, title/seniority mismatch, and experience mismatch?

## 4. System design

### 4.1 Inputs and entry points

- **Single-pair analysis:** one resume and one target job description; returns three model scores and evidence-based diagnosis.
- **Dataset ranking:** one candidate profile and the available job pool; ranks jobs using B0, B1, or B2. Evaluation uses only recorded pairs and a fixed candidate-grouped split.
- **Optional rewrite:** original resume, target job, detected gaps, and chosen prompting condition; returns a draft or an unavailable status if a local model is not configured.

### 4.2 Processing stages

1. **Input normalization:** trim whitespace and normalize text while preserving the original user-provided wording for display.
2. **Feature extraction:** word/character TF–IDF; optional Sentence-BERT embeddings; explicit skills from structured `clean_skills` where available, supplemented by conservative phrase matching for free text.
3. **Scoring:** B0 = TF–IDF cosine; B1 = Sentence-BERT cosine; B2 = B1 combined with skill overlap. The B2 skill weight is configurable and should be selected using validation candidates, not test data.
4. **Gap diagnosis:** report detected shared skills and job skills not found in resume. These are textual evidence signals, not statements about a person's actual abilities.
5. **Optional rewrite:** request rephrasing and organization only; do not add skills unless explicitly evidenced in original resume. Treat all output as untrusted until reviewed.
6. **Evaluation:** compare rankings to the provided compatibility score with NDCG@5/@10; inspect failure cases and manually review a small sample of rewrites.

### 4.3 Model variants

| Variant | Method | Purpose |
|---|---|---|
| B0 | TF–IDF + cosine similarity | Classical lexical baseline |
| B1 | Sentence-BERT + cosine similarity | Dense semantic baseline |
| B2 | B1 + explicit skill overlap | Test incremental value of skills |

B2 is a transparent combination rather than a learned ATS predictor. Any weights must be stated, tuned on validation candidates only, and frozen before test evaluation.

## 5. Dataset and data governance

The primary resource is `rahulrajpu676/job-resume-matching` on Hugging Face, described as containing 9,544 candidate profiles, 1,167 job postings, and 122,560 recorded compatibility pairs. The repository can read local reformatted CSV files or download source files when configured. Schema varies between versions, so column mapping must be checked before experiments.

The compatibility score and component fields are benchmark labels only. The component subscores must not become model inputs. Unrecorded pairs are unknown, not negative. Avoid publishing personal text, retain only the minimum necessary data, and do not expose uploaded resumes in logs or analytics.

## 6. Experimental plan

### 6.1 Ranking

- Evaluate B0–B2 on recorded candidate–job pairs.
- Split by candidate ID into train/validation/test groups where any tuning is performed, preventing resumes from one candidate appearing across partitions.
- Compute NDCG@5 and NDCG@10 per candidate on the fixed set of recorded jobs; aggregate with a clearly stated mean.
- Treat compatibility score as graded proxy relevance. Results describe agreement with that proxy and do not generalize to unrecorded jobs.
- Recall/MRR require an a-priori binary relevance threshold and are optional. Correlation with the proxy score is secondary.

### 6.2 Rewrite study

Select a small, documented sample and compare (R0) resume + job prompt against (R1) the same prompt plus diagnosed gaps, holding model, settings, and factual constraints constant. Rescore using the same text-matching functions, but report a score change rather than claiming outcome improvement. Human reviewers should independently flag unsupported claims and important omissions. Define unsupported-claim rate as reviewed rewrites containing at least one unsupported factual claim divided by all reviewed rewrites. Keep originals and generated versions for side-by-side audit only in a controlled environment.

### 6.3 Error analysis

Inspect selected examples of skill synonym misses, sparse resumes, title/seniority mismatch, and experience mismatch. Where ranking-position change is reported, rescore the whole fixed job pool before and after rewrite. Otherwise call it a compatibility-score change.

## 7. Interface and implementation

The project uses FastAPI for typed API boundaries and a Next.js web UI for a simple, responsive candidate workflow. The API and frontend are separate deployable modules. Optional Sentence-BERT and Ollama integrations are isolated so the baseline works without model downloads. The app does not persist uploaded text by default.

## 8. Expected outputs

- Reproducible B0/B1/B2 code and ranking metrics.
- Single-pair interface with scores, shared skills, and textual gaps.
- Optional locally hosted constrained rewrite with human-review warnings.
- Error-analysis examples and limitations documented alongside results.

## 9. Limitations and responsible use

Keyword matching misses synonyms and context; embeddings can blur specific requirements; skill extraction can be incomplete; compatibility labels may contain historical or dataset biases; and LLMs can still hallucinate despite constraints. The system cannot validate candidate truth, predict hiring decisions, or infer ability from missing text. It must not be used to screen, reject, rank, or make consequential decisions about real applicants.

## References

- Dataset: [rahulrajpu676/job-resume-matching](https://huggingface.co/datasets/rahulrajpu676/job-resume-matching)
- Lavi, D., Medentsiy, V., & Graus, D. (2021). *conSultantBERT: Fine-tuned siamese Sentence-BERT for matching jobs and job seekers*. https://doi.org/10.48550/arxiv.2109.06501
- Kaplan, E. A. et al. (2026). *Synapse: Evolving job-person fit with explainable two-phase retrieval and LLM-guided genetic resume optimization*. https://arxiv.org/abs/2604.02539v1
- Reference code: https://github.com/rufinachw/COMP7607-NLP-Resume-Optimizer
