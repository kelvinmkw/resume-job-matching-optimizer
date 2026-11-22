# Methodology and evaluation protocol

## Models

- **B0:** word/character TF–IDF vectors and cosine similarity.
- **B1:** Sentence-BERT cosine similarity (optional model dependency; document exact model and version).
- **B2:** B1 combined with explicit skill-set Jaccard overlap: `(1 - alpha) * B1 + alpha * overlap`. Freeze alpha after validation.

Scores are similarity signals, not calibrated probabilities. Do not label them hiring likelihoods or ATS percentages.

## Dataset ranking

1. Parse only recorded match rows and join resume/job text via IDs.
2. Group split by candidate ID if tuning any choices; avoid leakage across one candidate's records.
3. Rank each held-out candidate's fixed pool of recorded jobs independently under each model.
4. Compute NDCG@5 and NDCG@10 using the recorded overall compatibility score as graded proxy relevance.
5. Report pool construction, split seed, candidate counts, missing-text policy, model versions, and aggregation method.
6. Do not treat unrecorded pairs as irrelevant and do not feed component scores to the models.

## Rewrite evaluation

Compare original and rewritten compatibility scores using the same scoring implementation. A score increase is only textual alignment with that metric. To assess factuality, human reviewers should compare each sentence with the source resume and record unsupported claims and material omissions. An automated model must not certify factual truth. Report sample size and review protocol; avoid claiming statistical significance from a tiny convenience sample.

## Responsible interpretation

This benchmark does not represent ground-truth hiring outcomes, and historical data may reflect societal and organizational bias. The tool is not for screening or consequential decisions. Skill absence from text is not evidence that a person lacks the skill.
