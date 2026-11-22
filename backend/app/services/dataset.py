from pathlib import Path
import pandas as pd
from app.config import get_settings

class DatasetUnavailable(RuntimeError):
    pass

def load_jobs() -> pd.DataFrame:
    path = Path(get_settings().data_dir) / "job.csv"
    if not path.exists():
        raise DatasetUnavailable("job.csv not found; configure DATA_DIR and add the normalized dataset files")
    frame = pd.read_csv(path).fillna("")
    # Resolve common column aliases without assuming one dataset release schema.
    aliases = {"job_id": ["job_id", "id", "jobid"], "title": ["title", "job_title", "position"], "text": ["job_text", "description", "job_description", "text"], "skills": ["clean_skills", "skills", "required_skills"]}
    normalized = {c.lower().strip(): c for c in frame.columns}
    result = pd.DataFrame()
    for target, candidates in aliases.items():
        source = next((normalized[c] for c in candidates if c in normalized), None)
        result[target] = frame[source].astype(str) if source else (frame.index.astype(str) if target == "job_id" else "")
    return result
