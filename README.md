# Resume–Job Matching & Optimizer

An explainable NLP project for comparing a resume with a job description, highlighting evidenced and not-yet-evidenced skills, ranking recorded candidate–job pairs, and optionally generating a fact-constrained rewrite for human review.

> **Important:** This is an educational decision-support prototype, not an ATS, hiring recommendation, or guarantee of interview outcomes. A missing keyword means only that the skill was not found in the supplied text; it does not mean the candidate lacks the ability. Never submit generated changes without reviewing them.

## Project goals

- Compare lexical TF–IDF (B0), semantic Sentence-BERT (B1), and semantic plus explicit skill overlap (B2).
- Diagnose matching dimensions and skill gaps transparently.
- Support dataset-wide ranking using the provided compatibility score only as a proxy relevance label.
- Offer optional Ollama rewriting with explicit no-invention constraints and human factuality review.
- Make assumptions, limitations, and evaluation methodology reproducible.

## Repository map

```text
backend/                 FastAPI API and matching/diagnosis/rewrite services
frontend/                Next.js interface (resume + job analysis and ranking)
data/                    Place reformatted cv.csv, job.csv, matches.csv here
scripts/                 Dataset preparation and evaluation entry points
docs/                    Detailed proposal, methodology, data guide, API notes
notebooks/               Space for exploratory analysis and course experiments
tests/                   Backend unit tests
```

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: <http://localhost:8000/docs>. By default, the API uses a lightweight TF–IDF backend. Install the optional semantic dependencies and set `MATCHER_USE_SENTENCE_TRANSFORMERS=true` to enable Sentence-BERT; the model is downloaded on first use.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:3000>. Set `NEXT_PUBLIC_API_URL=http://localhost:8000` if using a non-default API URL.

### Dataset

Put the reference dataset's reformatted CSV files at `data/cv.csv`, `data/job.csv`, and `data/matches.csv`. See [docs/DATA.md](docs/DATA.md). The app works for a single resume/job pair without those files. Do not commit private or identifiable resume data.

### Optional local LLM rewriting

Install Ollama separately, pull an instruction model (for example `ollama pull llama3`), then set `OLLAMA_ENABLED=true` and `OLLAMA_MODEL=llama3`. Without Ollama, the rewrite endpoint returns an explicit unavailable status; it does not fabricate a rewrite. A model's compliance is not proof of factual accuracy.

## Main endpoints

- `GET /health` — service status.
- `POST /api/analyze` — B0/B1/B2 scores, skill evidence and gap diagnosis.
- `POST /api/rank` — rank dataset jobs for a resume (requires CSV data).
- `POST /api/rewrite` — optional constrained rewrite proposal, requires Ollama.

See [docs/API.md](docs/API.md) for request examples.

## Evaluation overview

For dataset-wide experiments, treat the dataset's compatibility score as a proxy relevance signal, not a human hiring judgment. Evaluate NDCG@5 and NDCG@10 over recorded candidate–job pairs and split by candidate ID when tuning weights or comparing configurations. Unrecorded pairs are not negative examples. Do not use precomputed component subscores as model inputs. Report ranking results only for the fixed, clearly stated job pool. Rewriting score changes are not evidence of improved hiring outcomes.

## Development and tests

```bash
cd backend && pytest
```

The implementation is modular by responsibility. See [docs/PROJECT_PROPOSAL.md](docs/PROJECT_PROPOSAL.md) for the detailed project design and [docs/METHODOLOGY.md](docs/METHODOLOGY.md) for evaluation decisions.

## References

- Dataset: [rahulrajpu676/job-resume-matching](https://huggingface.co/datasets/rahulrajpu676/job-resume-matching)
- Lavi, D. et al. (2021). [conSultantBERT](https://doi.org/10.48550/arxiv.2109.06501)
- Reference implementation and course draft: [rufinachw/COMP7607-NLP-Resume-Optimizer](https://github.com/rufinachw/COMP7607-NLP-Resume-Optimizer)
- Frontend inspiration: [ivan00105/Agentic-System-for-Investment-Research](https://github.com/ivan00105/Agentic-System-for-Investment-Research)

## License and data notice

No third-party dataset or pretrained model weights are bundled. Follow the dataset and model licenses and cite them in coursework. Add a suitable project license after confirming group requirements.
