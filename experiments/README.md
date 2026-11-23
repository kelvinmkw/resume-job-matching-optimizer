# Experimental work incorporated from the groupmate's experiments

This folder collects the proposal-aligned dataset matching experiment in a clean, reproducible form. It is not a blind copy of the experiment workspace: full CSVs, model caches, candidate-level results, human-review case text, and generated resume drafts are deliberately excluded.

## Relevance assessment

| Work area | Relevance to proposal | Decision |
|---|---|---|
| `matching_baselines` | Directly evaluates B0 TF–IDF, B1 Sentence-BERT, and B2 skill-aware matching. | Incorporate the ranking metric definitions and document the baseline protocol. |
| `grouped_matching_baselines` | Directly improves the evaluation design after finding that candidate IDs can share source resume content across splits. | Incorporate source-core grouping/audit and a candidate-grouped evaluation runner. Treat core matching as a heuristic, not verified identity. |
| `optimizer_integration` | Directly supports optional constrained rewriting, rescoring, and factuality review. | Incorporate a portable single-sentence proposal validator and clearly document that it is only a conservative heuristic requiring human review. Do not copy dependent local artifacts or imply factual verification. |

## Why source grouping matters

The supplied experiment summary reports shared structural resume cores across candidate-ID splits. Its later source-group-disjoint experiment has 5,603 train, 1,902 validation, and 1,859 test paired candidates, in 202, 67, and 68 heuristic source groups. This is a material methodological qualification: candidate-ID disjointness alone is not enough to claim source-resume independence.

The reported grouped metrics and uncertainty intervals are transcribed in `grouped_matching_baselines/REPORTED_RESULTS.md`; they are not rerun by this commit because the input CSVs and frozen run artifacts are not in this repository. Reproduce the experiment locally before presenting those values as independently verified.

## Running the grouped experiment

From the repository root, install the optional experiment dependencies:

```bash
python -m pip install -r experiments/requirements.txt
```

Download the data as described in `data/README.md`, then run:

```bash
python experiments/grouped_matching_baselines/run.py \
  --data-dir data --output-dir experiments/grouped_matching_baselines/outputs
```

The runner writes membership manifests, data hashes, metrics and audit JSON to the ignored output directory. It does not save raw resume text. Check the exact input hashes and grouping coverage before interpreting results. A source core is a heuristic grouping key, not proof of applicant identity; incomplete profiles are excluded from paired evaluation and may differ systematically.

## Rewriting work

See `optimizer_integration/README.md` and `optimizer_integration/evidence_bound_edit.py`. The validator accepts one explicitly selected sentence span at a time; it does not call an LLM, certify truth, or replace human comparison with the source resume. Whole-resume rewriting and the experimental local model remain optional extensions.
