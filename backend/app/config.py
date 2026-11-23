from pathlib import Path
import os

# Resolve data path relative to the repository, independent of the launch cwd.
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"

class Settings:
    app_name: str = os.getenv("APP_NAME", "Resume Job Matching API")
    cors_origins: list[str] = [item.strip() for item in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if item.strip()]
    data_dir: str = os.getenv("DATA_DIR", str(DEFAULT_DATA_DIR))
    matcher_use_sentence_transformers: bool = os.getenv("MATCHER_USE_SENTENCE_TRANSFORMERS", "false").lower() == "true"
    sentence_transformer_model: str = os.getenv("SENTENCE_TRANSFORMER_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    ollama_enabled: bool = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    skill_weight: float = float(os.getenv("SKILL_WEIGHT", "0.25"))

