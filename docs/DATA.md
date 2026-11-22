# Data guide

## Expected local files

Put dataset files here (do not commit confidential resumes):

```text
data/cv.csv
 data/job.csv
 data/matches.csv
```

The leading whitespace above is illustrative only; actual paths have no leading space. The reference repository also contains `reformatted_data/job_education.csv`; inspect its schema before using it.

The dataset is available at [Hugging Face](https://huggingface.co/datasets/rahulrajpu676/job-resume-matching). This project intentionally does not download the full dataset automatically at API startup. Download manually or implement a controlled data preparation step, verify the dataset license and version, and place the normalized files in `data/`.

## Schema mapping

Dataset releases may vary. Before analysis, inspect headers and map fields to these conceptual columns:

- CV: candidate identifier, resume/profile text, optional structured skills.
- Job: job identifier, title, description, optional structured skills.
- Matches: candidate identifier, job identifier, continuous compatibility score.

Never use precomputed component sub-scores (semantic, skill, title, category, experience, education, or similar) as model input features. The overall compatibility score is a proxy relevance label for ranking evaluation only. Do not treat unrecorded candidate–job combinations as negatives.

## Privacy and handling

Use synthetic or permitted data for demos. Avoid committing identifiable resume text, tokens, private annotations, or raw user uploads. The live API does not persist uploaded content. If you add storage, obtain consent, define retention/deletion controls, secure access, and document the change.
