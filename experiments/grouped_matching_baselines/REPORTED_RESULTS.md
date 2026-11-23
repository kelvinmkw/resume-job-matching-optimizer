# Grouped matching baselines: reported result snapshot

This report summarizes the groupmate-provided `EVALUATION_SUMMARY.json`. The source data, source files, exact outputs, and run environment were not available in this repository at the time this summary was added. These numbers are therefore **reported results, not independently reproduced results**.

## Split and coverage reported

| Split | Paired candidates | Heuristic source groups |
|---|---:|---:|
| Train | 5,603 | 202 |
| Validation | 1,902 | 67 |
| Test | 1,859 | 68 |

The supplied audit reports 9,544 CV profiles, 9,376 with a structural core, 337 exact structural source groups, 9,364 eligible paired candidates, and 168 paired candidates excluded for missing/incomplete core. No core group crosses the stored train/validation/test partitions. The core compares normalized objective, education lists, and employment title/date lists. It is heuristic shared-content evidence, not identity verification. Near duplicates, common templates, and same-person different-core records may remain.

## Test ranking results reported

Means are candidate-weighted NDCG over each candidate's recorded jobs. Parentheses are reported 95% source-group bootstrap percentile intervals.

| Model | NDCG@5 | NDCG@10 |
|---|---:|---:|
| Uniform random expectation | 0.957554 (0.953850–0.960937) | 0.972028 (0.969078–0.974619) |
| B0: TF–IDF cosine | 0.963325 (0.959622–0.966798) | 0.975795 (0.972963–0.978298) |
| B1: MiniLM cosine | 0.964698 (0.961034–0.967888) | 0.976900 (0.974191–0.979303) |
| B2: semantic + skill overlap | 0.969081 (0.966592–0.971430) | 0.979666 (0.977880–0.981355) |
| Paired B2 − B1 | +0.004384 (+0.001643–+0.008089) | +0.002765 (+0.001046–+0.005144) |

Validation selected B2 skill weight alpha = 0.60 on a 21-point grid, maximizing validation NDCG@10, with ties preferring the larger alpha. Test was then evaluated with that frozen weight. The supplied result metadata names `sentence-transformers/all-MiniLM-L6-v2` revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, max sequence length 256, seed 42, and 2,000 source-group bootstrap draws.

## Interpretation limits

- Compatibility scores are constructed proxy labels, not human relevance or hiring outcomes.
- The dataset contains selected/recorded pairs; unlisted pairs are unknown, not negatives. NDCG is over each candidate's recorded job pool, not the full catalog.
- High random NDCG is expected in short, restricted positive-only lists. Interpret gains relative to the random baseline, not the raw near-one values alone.
- Skill and semantic features may overlap the compatibility-score construction recipe. Better agreement with that proxy does not independently prove better job matching.
- Source cores are heuristic; their coverage and false-match/missed-match behavior need further validation. Excluded profiles may be systematically different.
- Candidate-group bootstrap intervals condition on the chosen split and alpha and do not capture split, model, or grouping uncertainty.
- Rewriting score gains are a separate question and were not evaluated by these ranking metrics.

For reproducible execution, use `run.py` after downloading the dataset. Its output and membership manifests are ignored by Git because they can contain candidate IDs and local data provenance.
