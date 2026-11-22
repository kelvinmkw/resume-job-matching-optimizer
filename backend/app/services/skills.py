import re
from collections.abc import Iterable

# Conservative phrase matching: this is a transparent baseline, not a complete skill ontology.
def normalize_skill(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())

def find_skills(text: str, supplied: Iterable[str] = ()) -> set[str]:
    text_l = text.lower()
    found = {normalize_skill(s) for s in supplied if s.strip() and normalize_skill(s) in text_l}
    # Add a small demo vocabulary; dataset-provided structured skills are preferred.
    vocabulary = ["python", "sql", "java", "javascript", "typescript", "machine learning", "deep learning", "data analysis", "data pipelines", "aws", "azure", "gcp", "docker", "kubernetes", "communication", "project management", "excel", "power bi", "tableau", "ollama", "sentence-bert"]
    for skill in vocabulary:
        if re.search(r"(?<!\w)" + re.escape(skill) + r"(?!\w)", text_l):
            found.add(skill)
    return found

def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0
