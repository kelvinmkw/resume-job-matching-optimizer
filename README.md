# Resume–Job Matching & Optimizer

An explainable NLP project for comparing a resume with a job description, highlighting detected evidence and textual skill gaps, ranking recorded candidate–job pairs, and optionally generating a fact-constrained rewrite for human review.

> **Important:** This is an educational prototype, not an ATS, hiring recommendation, or guarantee of interview outcomes. A missing keyword means only that the skill was not found in the supplied text; it does not mean the candidate lacks the ability. Review every generated change.

## Repository map

```text
backend/       FastAPI API and matching/diagnosis/rewrite services, with backend tests
frontend/      Next.js web application
 data/         Put local cv.csv, job.csv, matches.csv here (not committed)
scripts/       Dataset ranking evaluation script and usage guide
docs/          Project proposal, methodology, data guide, API notes
notebooks/     Dataset exploration notebook and notebook dependencies
```

## Quick start

Prerequisites: Python 3.10+ and Node.js 18+. Start the API and frontend in two terminals from the repository root.

### Terminal 1 — backend

```bash
cd backend
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Leave the API running. Open <http://localhost:8000/docs> for interactive API documentation.

### Terminal 2 — frontend

```bash
cd frontend
npm install
# Optional: copy .env.example to .env.local; default API URL is http://localhost:8000
npm run dev
```

Leave the frontend running and open <http://localhost:3000>. Paste resume and job-description text for single-pair analysis. This basic workflow does not require the dataset, Sentence-BERT, or Ollama.

### Dataset-wide evaluation (optional)

Download data as described in [`data/README.md`](data/README.md). With Python dependencies installed, run from the repository root:

```bash
python scripts/evaluate_ranking.py --cv data/cv.csv --jobs data/job.csv --matches data/matches.csv --output reports/ranking_metrics.csv
```

For the exploratory notebook, install its dependencies and launch Jupyter from the repository root:

```bash
pip install -r backend/requirements.txt
pip install -r notebooks/requirements.txt
jupyter lab
```

Then open `notebooks/01_dataset_exploration.ipynb`. Dataset files must be present for data cells.

### Optional features

- **Sentence-BERT:** install `sentence-transformers`, set `MATCHER_USE_SENTENCE_TRANSFORMERS=true` and `SENTENCE_TRANSFORMER_MODEL` in the backend environment. The model downloads on first use. Check `/health` and `b1_semantic`; an unavailable embedding is not a semantic score.
- **Local rewrite:** install Ollama separately, pull an instruction model (for example `ollama pull llama3`), and configure `OLLAMA_ENABLED=true` and `OLLAMA_MODEL=llama3`. Review generated text for unsupported claims.

## Main endpoints

- `GET /health` — service status.
- `POST /api/analyze` — B0/B1/B2 similarity signals and skill evidence.
- `POST /api/rank` — rank loaded jobs for a resume (requires `data/job.csv`).
- `POST /api/rewrite` — optional constrained rewrite proposal (requires Ollama).

See [docs/API.md](docs/API.md), [docs/PROJECT_PROPOSAL.md](docs/PROJECT_PROPOSAL.md), and [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Evaluation interpretation

The dataset compatibility score is a proxy relevance label, not a human hiring judgment. Evaluate NDCG@5/@10 on recorded candidate–job pairs; use candidate-grouped validation/test splits when tuning. Unrecorded pairs are unknown, not negatives. Dataset component subscores are not model inputs. Metrics indicate agreement with the proxy labels on the stated pool, not hiring performance.

## Tests

```bash
cd backend
pytest
```

## References

- Dataset: [rahulrajpu676/job-resume-matching](https://huggingface.co/datasets/rahulrajpu676/job-resume-matching)
- Lavi, D. et al. (2021). [conSultantBERT](https://doi.org/10.48550/arxiv.2109.06501)
- Reference implementation: [rufinachw/COMP7607-NLP-Resume-Optimizer](https://github.com/rufinachw/COMP7607-NLP-Resume-Optimizer)
- Frontend inspiration: [ivan00105/Agentic-System-for-Investment-Research](https://github.com/ivan00105/Agentic-System-for-Investment-Research)

No dataset or pretrained model weights are bundled. Follow current data/model terms and cite sources. Add a project license after confirming group requirements.
