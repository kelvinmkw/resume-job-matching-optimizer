# API guide

Base URL: `http://localhost:8000`. Interactive OpenAPI docs: `/docs`.

## Analyze a resume/job pair

```json
POST /api/analyze
{
  "resume_text": "Python developer with experience building data pipelines...",
  "job_text": "We are seeking a Python engineer with SQL and cloud experience...",
  "resume_skills": ["Python", "data pipelines"],
  "job_skills": ["Python", "SQL", "cloud"]
}
```

Returns B0/B1/B2 similarity signals, detected shared skills and skills not evidenced in resume, and explanatory caveats.

## Rank dataset jobs

```json
POST /api/rank
{
  "resume_text": "...",
  "model": "B2",
  "limit": 10
}
```

Requires data CSVs configured in the backend. Rankings cover only the loaded job pool and are not hiring recommendations.

## Rewrite

`POST /api/rewrite` accepts `resume_text`, `job_text`, `missing_skills` and `mode` (`unguided` or `gap_guided`). Ollama must be configured. Generated output is a draft and must be reviewed. No source resume evidence is silently added by application code.
