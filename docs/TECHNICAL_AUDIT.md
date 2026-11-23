# Experiment technical audit — 2026-11-23

## Scope and verification limits

Static audit of the app, notebook, ranking scripts, metrics, grouping code, and rewrite validator. The repository does not include the dataset CSVs, so dataset-backed runs and model downloads could not be performed here. Do not interpret static inspection as a successful end-to-end execution.

## Findings and fixes

### Notebook was not a Jupyter notebook

`notebooks/01_dataset_exploration.ipynb` previously contained Markdown prose rather than nbformat JSON. It could not be opened as a notebook. Replaced with a valid nbformat 4 notebook using cells for local dataset loading, flexible column resolution, joining recorded pairs, proxy-label summary/plot, optional structured-skill summary, and one TF–IDF example. It avoids printing resume text and does not use component subscores as features. Added Matplotlib to notebook dependencies. The notebook requires the three local CSVs and gives a clear missing-data error.

The supplied reference `01_eda.ipynb` is useful as a guide to exploratory topics, but was not copied directly: it materializes a large merged table, prints resume/job content, assumes specific headers, and inspects dataset-provided component subscores. Those choices conflict with this project's privacy and feature-isolation rules.

### Grouped baseline had reporting and edge-case defects

The grouped runner previously reported only NDCG@10, despite the planned @5/@10 reporting. It now calculates both, includes paired B2−B1 differences and handles undefined NDCG values. It now checks empty files, missing schema columns, empty training text, and model initialization errors. The source-group bootstrap's dead/incorrect empty-generator expression was removed and missing core mappings are checked.

B2 is `alpha * normalized semantic similarity + (1 - alpha) * job-skill coverage`; alpha is the semantic weight. TF–IDF is fitted on training resume/job text and scores a candidate against a shared job pool. These changes mean new results may differ from the previously supplied aggregate snapshot. The snapshot is explicitly not reproduced by this repository.

### Backend startup and ranking issues

- Removed an unused `pydantic_settings` import from `backend/app/__init__.py`; it was not a declared dependency and could prevent importing the API.
- Made the default data directory resolve from the repository path rather than the current working directory.
- Added `clean_skills_json` support to job CSV loading and parse its JSON list rather than comma-splitting encoded skills.
- Added batch ranking through one shared TF–IDF fit over the resume and all loaded jobs. Previously, the rank route called a pair matcher that refit TF–IDF separately for every job, making lexical scores across jobs inconsistent.
- Selecting B1 while embeddings are disabled now returns a clear 503 instead of silently substituting B0.

## Remaining caveats

- The backend's B2 skill feature is Jaccard overlap across detected skill sets, while the grouped experiment's skill feature is job-skill coverage. They are distinct implementations and should be documented/compared as such.
- Pairwise TF–IDF in `/api/analyze` is a local pair similarity, not a calibrated or cross-pair comparable score. The ranking route uses shared vocabulary across the loaded pool.
- `/api/rewrite` uses prompt constraints only. It is not connected to the experimental evidence-bound validator and does not automatically verify output. Human review remains mandatory.
- The simple `scripts/evaluate_ranking.py` uses candidate-ID grouping, not structural source grouping. Prefer `experiments/grouped_matching_baselines/run.py` for the source-overlap-controlled experiment.
- Structural source-core grouping is a heuristic, not verified person identity. Ineligible profiles may differ systematically.
- Frontend build, Python suites, notebook execution, CSV compatibility and model-download paths were not executable in this static audit environment. Run the commands below locally after downloading data.

## Verification commands

From the repository root:

```bash
python -m unittest discover -s experiments/grouped_matching_baselines -p 'test_*.py'
python -m unittest discover -s experiments/matching_baselines -p 'test_*.py'
python -m unittest discover -s experiments/optimizer_integration -p 'test_*.py'
cd backend && pytest
cd ../frontend && npm install && npm run build
```

For the notebook, install backend and notebook requirements, start Jupyter from the repository root, and run all cells after downloading `data/cv.csv`, `data/job.csv`, and `data/matches.csv`. Never commit resume contents, generated full-text drafts, or local experiment membership/output artifacts.
