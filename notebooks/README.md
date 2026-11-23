# Notebooks

`01_dataset_exploration.ipynb` is the project's runnable exploratory notebook. It checks files and schema without printing resume text, joins the recorded pairs, summarizes the compatibility proxy label, and demonstrates a small TF–IDF plus skill-overlap example. This notebook is for exploration, not final benchmark results; use `scripts/evaluate_ranking.py` for grouped NDCG evaluation.

Download data per [`data/README.md`](../data/README.md). From the repository root, install `backend/requirements.txt` and `notebooks/requirements.txt`, run `jupyter lab`, and open the notebook. Do not commit notebook outputs containing personal or sensitive data.
