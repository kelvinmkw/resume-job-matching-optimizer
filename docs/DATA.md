# Data guide

## Download and file placement

The dataset is not bundled because of its size and the need to follow its current terms. Download it from [rahulrajpu676/job-resume-matching](https://huggingface.co/datasets/rahulrajpu676/job-resume-matching), review the dataset card/license, and place the relevant files locally as `data/cv.csv`, `data/job.csv`, and `data/matches.csv`. Detailed steps are in [`data/README.md`](../data/README.md). CSVs are git-ignored.

## Expected schema

Dataset releases may vary. The evaluator recognizes common aliases for these conceptual columns:

- CV: candidate identifier, resume/profile text, optional structured skills.
- Job: job identifier, title, description, optional structured skills.
- Matches: candidate identifier, job identifier, continuous overall compatibility score.

The API's `/api/rank` currently reads the local `job.csv` and recognizes common job id/title/text/skill columns. Inspect CSV headers if the source format differs; normalize locally without publishing resume contents.

Never use precomputed component subscores (semantic, skill, title, category, experience, education, or similar) as model input features. The overall compatibility score is a proxy relevance label for ranking evaluation only. Do not treat unrecorded candidate–job combinations as negatives.

## Privacy and handling

Use synthetic or permitted data for demos. Avoid committing identifiable resume text, tokens, private annotations, or raw user uploads. The live API does not persist uploaded content. If storage is added, obtain consent, define retention/deletion controls, secure access, and document the change.
