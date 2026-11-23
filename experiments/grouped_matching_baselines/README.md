# Source-group-disjoint evaluation

This experiment is relevant to the proposal's dataset-wide ranking question and provides a corrective grouping protocol after the groupmate's audit found shared structural resume content across candidate-ID splits.

## Run

From the repository root:

```bash
python -m pip install -r experiments/requirements.txt
python experiments/grouped_matching_baselines/run.py --data-dir data --output-dir experiments/grouped_matching_baselines/outputs
```

The runner uses the expected structured CV columns `resume_text`, `education_text`, `experience_text`; job description/title and skill columns; and recorded pair IDs plus an overall score. It recognizes common aliases and gives an actionable error for missing required fields. Review the input headers first if your reformatted dataset differs.

The runner creates deterministic 60/20/20 partitions of structural source-core hashes (seed 42), tunes B2 alpha on validation NDCG@10 only, then evaluates the selected value on test. B0 vocabulary/IDF are fit on training candidate and job text. B1 uses a pinned Sentence-Transformer revision. B2 combines normalized semantic cosine and job-skill coverage. NDCG uses linear gain for the continuous compatibility score and average tie ranks; it also computes an exact expected random ranking baseline. Confidence intervals resample complete source groups and remain conditional on the fixed split/model/weight.

The source fingerprint's objective/education/history heuristic is not an identity detector. Eligible coverage is incomplete. Report the exclusions and limitations rather than claiming unseen-person generalization. Scores are proxy-label agreement on recorded pairs, not hiring success.

The user-provided aggregate snapshot is in `REPORTED_RESULTS.md`, explicitly marked not independently reproduced. Re-run before relying on it. Run grouping and metric unit tests with:

```bash
python -m unittest discover -s experiments/grouped_matching_baselines -p 'test_*.py'
python -m unittest discover -s experiments/matching_baselines -p 'test_*.py'
```
