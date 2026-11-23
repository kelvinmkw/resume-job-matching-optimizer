# Resume–Job Matching & Optimizer

An explainable NLP project for comparing a resume with a job description, highlighting detected evidence and textual skill gaps, ranking recorded candidate–job pairs, and optionally generating a fact-constrained rewrite for human review.

> **Important:** This is an educational prototype, not an ATS, hiring recommendation, or guarantee of interview outcomes. A missing keyword means only that the skill was not found in the supplied text; it does not mean the candidate lacks the ability. Review every generated change.

## Repository map

```text
backend/       FastAPI API and matching/diagnosis/rewrite services, with tests
frontend/      Next.js web application
data/          Put local cv.csv, job.csv, matches.csv here (not committed)
scripts/       Simpler candidate-ID split ranking evaluation
experiments/   Source-grouped baselines, metrics, rewrite-validation research
notebooks/     Dataset exploration notebook and dependencies
docs/          Project proposal, methodology, data guide, API notes, technical audit
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

Keep the API running. Interactive docs are at <http://localhost:8000/docs>.

### Terminal 2 — frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:3000>. Single-pair analysis works without dataset files. Ranking requires local job data; Sentence-BERT and Ollama rewriting are optional.

## Dataset exploration and experiments

Download the data as described in [`data/README.md`](data/README.md). To run the notebook, from the repository root:

```bash
python -m pip install -r backend/requirements.txt
python -m pip install -r notebooks/requirements.txt
jupyter lab
```

Open `notebooks/01_dataset_exploration.ipynb` and run cells top-to-bottom. The notebook expects the three CSV files locally and does not print raw resume text.

Recommended source-group-disjoint ranking experiment:

```bash
python -m pip install -r experiments/requirements.txt
python experiments/grouped_matching_baselines/run.py --data-dir data --output-dir experiments/grouped_matching_baselines/outputs
```

The structural source grouping is heuristic and incomplete, not verified identity. Metrics measure agreement with the dataset proxy labels on recorded pairs only. See [`experiments/grouped_matching_baselines/README.md`](experiments/grouped_matching_baselines/README.md). The supplied results snapshot is not independently reproduced; rerun before citing as repository results.

## API endpoints

- `GET /health` — service status.
- `POST /api/analyze` — B0/B1/B2 similarity signals and skill evidence.
- `POST /api/rank` — rank loaded jobs for a resume (requires `data/job.csv`).
- `POST /api/rewrite` — optional local rewrite draft (requires Ollama); output is not automatically fact-checked.

See the project proposal, methodology, API guide, and [technical audit](docs/TECHNICAL_AUDIT.md).

## Responsible interpretation

Compatibility scores are proxy labels, not human hiring judgments. Unrecorded pairs are unknown, not negatives. Dataset component subscores are not model input features. Do not use this prototype for screening or consequential hiring decisions. Never commit private resume text or local experiment outputs.
