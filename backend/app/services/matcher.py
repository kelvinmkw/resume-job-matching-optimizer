from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import get_settings

class Matcher:
    def __init__(self):
        self._encoder = None
        self._encoder_attempted = False

    def _semantic_score(self, left: str, right: str) -> float | None:
        cfg = get_settings()
        if not cfg.matcher_use_sentence_transformers:
            return None
        if not self._encoder_attempted:
            self._encoder_attempted = True
            try:
                from sentence_transformers import SentenceTransformer
                self._encoder = SentenceTransformer(cfg.sentence_transformer_model)
            except (ImportError, OSError, RuntimeError):
                self._encoder = None
        if self._encoder is None:
            return None
        vectors = self._encoder.encode([left, right], normalize_embeddings=True)
        return float(vectors[0] @ vectors[1])

    def score(self, resume: str, job: str, resume_skills: set[str], job_skills: set[str]) -> dict:
        try:
            matrix = TfidfVectorizer(ngram_range=(1, 2), stop_words="english").fit_transform([resume, job])
            lexical = float(cosine_similarity(matrix[0], matrix[1])[0, 0])
        except ValueError:
            lexical = 0.0
        semantic = self._semantic_score(resume, job)
        # B1 falls back to lexical only when the optional embedding model is unavailable;
        # response indicates null so the fallback is not mistaken for Sentence-BERT output.
        base = semantic if semantic is not None else lexical
        skill = len(resume_skills & job_skills) / len(resume_skills | job_skills) if resume_skills | job_skills else 0.0
        alpha = get_settings().skill_weight
        return {"b0_tfidf": lexical, "b1_semantic": semantic, "b2_semantic_skill": (1-alpha)*base + alpha*skill, "skill_overlap": skill}

@lru_cache
def get_matcher() -> Matcher:
    return Matcher()
