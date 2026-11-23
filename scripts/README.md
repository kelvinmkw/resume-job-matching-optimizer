# Evaluation scripts

Download the dataset and place the files in `data/` as described in [`data/README.md`](../data/README.md). Install Python dependencies (`pip install -r backend/requirements.txt`) and run from the repository root:

```bash
python scripts/evaluate_ranking.py \
  --cv data/cv.csv --jobs data/job.csv --matches data/matches.csv \
  --test-fraction 0.2 --seed 42 --output reports/ranking_metrics.csv
```

Optional Sentence-BERT:

```bash
pip install sentence-transformers
python scripts/evaluate_ranking.py --sentence-transformer sentence-transformers/all-MiniLM-L6-v2
```

The CLI maps common column aliases and reports available columns if schema adjustment is needed. Without a Sentence-BERT model B1 falls back to lexical scores and the output labels this; do not describe that fallback as Sentence-BERT. Tune B2's skill weight on validation candidates and freeze it before test reporting.

Metrics use each test candidate's recorded jobs only. Compatibility scores are graded proxy relevance labels; component subscores are not features; unrecorded pairs are not negative examples. Results describe agreement with the dataset proxy labels, not hiring performance.
