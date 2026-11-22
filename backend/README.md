# Backend

FastAPI service implementing feature extraction, similarity scoring, diagnosis, dataset ranking, and optional rewrite provider.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Configure with environment variables described in `.env.example`. The baseline works without Sentence-BERT or Ollama.
