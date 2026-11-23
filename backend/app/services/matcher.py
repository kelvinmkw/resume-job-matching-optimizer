from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import get_settings

class Matcher:
    def __init__(self):
        self._encoder = None
        self._encoder_attempted = False

    def _load_encoder(self):
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
        return self._encoder

    def _semantic_score(self, left: str, right: str) -> float | None:
        encoder = self._load_encoder()
        if encoder is None:
            return None
        vectors = encoder.encode([left, right], normalize_embeddings=True)
        return float(vectors[0] @ vectors[1])

    @staticmethod
    def _lexical_scores(resume: str, jobs: list[str]) -> list[float]:
        if not jobs:
            return []
        documents = [resume] + jobs
        try:
            matrix = TfidfVectorizer(ngram_range=(1, 2), stop_words="english").fit_transform(documents)
            return cosine_similarity(matrix[0:1], matrix[1:]).ravel().astype(float).tolist()
        except ValueError:
            return [0.0] * len(jobs)

    def score_many(self, resume: str, jobs: list[str], resume_skills: set[str], job_skills: list[set[str]]) -> dict:
        """Score one resume against a shared job pool with a single TF-IDF space."""
        if len(jobs) != len(job_skills):
            raise ValueError("jobs and job_skills must have equal length")
        lexical = self._lexical_scores(resume, jobs)
        semantic = None
        encoder = self._load_encoder()
        if encoder is not None and jobs:
            vectors = encoder.encode([resume] + jobs, normalize_embeddings=True)
            semantic = (vectors[1:] @ vectors[0]).astype(float).tolist()
        overlaps = [len(resume_skills & skills) / len(resume_skills | skills) if resume_skills | skills else 0.0 for skills in job_skills]
        alpha = get_settings().skill_weight
        base = semantic if semantic is not None else lexical
        return {"b0_tfidf": lexical, "b1_semantic": semantic,
                "b2_semantic_skill": [(1-alpha)*base[i] + alpha*overlaps[i] for i in range(len(jobs))],
                "skill_overlap": overlaps}

    def score(self, resume: str, job: str, resume_skills: set[str], job_skills: set[str]) -> dict:
        result = self.score_many(resume, [job], resume_skills, [job_skills])
        return {key: (value[0] if isinstance(value, list) and value else None) for key, value in result.items()}

@lru_cache
def get_matcher() -> Matcher:
    return Matcher()
