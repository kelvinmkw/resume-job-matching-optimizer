from pathlib import Path
import json
import pandas as pd
from app.config import get_settings

class DatasetUnavailable(RuntimeError):
    pass

def _parse_skill_list(value):
    if value is None:
        return []
    raw = str(value).strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        parsed = [part.strip().strip("\\\"'") for part in raw.strip("[]").split(",")]
    if isinstance(parsed, str):
        parsed = [parsed]
    if not isinstance(parsed, list):
        return []
    return [str(item).strip() for item in parsed if str(item).strip()]

def load_jobs() -> pd.DataFrame:
    path = Path(get_settings().data_dir).expanduser() / "job.csv"
    if not path.is_file():
        raise DatasetUnavailable(f"job.csv not found at {path}; set DATA_DIR or follow data/README.md")
    frame = pd.read_csv(path, low_memory=False).fillna("")
    if frame.empty:
        raise DatasetUnavailable(f"job.csv has a header but no job rows: {path}")
    aliases = {
        "job_id": ["job_id", "id", "jobid"],
        "title": ["title", "job_title", "position"],
        "text": ["job_text", "description", "job_description", "text"],
        "skills": ["clean_skills_json", "clean_skills", "skills", "required_skills"],
    }
    normalized = {str(column).lower().strip(): column for column in frame.columns}
    resolved = {target: next((normalized[name] for name in candidates if name in normalized), None)
                for target, candidates in aliases.items()}
    if resolved["text"] is None:
        raise DatasetUnavailable(f"No job description column found in {path}; available columns: {list(frame.columns)}")
    result = pd.DataFrame(index=frame.index)
    result["job_id"] = frame[resolved["job_id"]].astype(str) if resolved["job_id"] else frame.index.astype(str)
    result["title"] = frame[resolved["title"]].astype(str) if resolved["title"] else ""
    result["text"] = frame[resolved["text"]].astype(str)
    result["skills"] = frame[resolved["skills"]].map(_parse_skill_list) if resolved["skills"] else [[] for _ in range(len(frame))]
    return result.reset_index(drop=True)
