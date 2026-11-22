# Evaluation scripts

## Candidate-grouped ranking metrics

Install backend requirements (pandas and scikit-learn) and run from repository root:

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

The CLI maps common column aliases but will stop with available column names when the dataset schema needs an explicit adjustment. B1 is reported as lexical fallback if no Sentence-BERT model is provided; the output records this. Tune B2's `--skill-weight` on validation candidates and freeze it before test reporting.

Metrics use each test candidate's recorded jobs only. Compatibility scores are graded proxy relevance labels; component subscores are not features; unrecorded pairs are not negative examples. Results do not measure hiring outcomes.
