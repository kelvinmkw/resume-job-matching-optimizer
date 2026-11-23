# Notebook setup

`01_dataset_exploration.ipynb` is a valid nbformat 4 Jupyter notebook. It expects local `data/cv.csv`, `data/job.csv`, and `data/matches.csv`; see [`data/README.md`](../data/README.md).

From the repository root:

```bash
python -m pip install -r backend/requirements.txt
python -m pip install -r notebooks/requirements.txt
jupyter lab
```

Open `notebooks/01_dataset_exploration.ipynb`. It also finds the dataset when Jupyter is started from the `notebooks/` directory. It does not print raw resume or job text. The dataset and model results are exploratory and should not be interpreted as hiring outcomes.
