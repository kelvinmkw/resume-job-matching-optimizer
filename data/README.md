# Dataset download and setup

The full dataset is intentionally not committed because it is large and includes resume/profile text. Download it locally from the official [Hugging Face dataset page](https://huggingface.co/datasets/rahulrajpu676/job-resume-matching), first reviewing its current dataset card, license, and terms.

## Steps

1. Open **Files and versions** on the dataset page and download the CV, job, and match CSV files (or follow the dataset card's documented download method).
2. If downloaded as an archive, extract it locally.
3. Copy/rename the appropriate files to these paths:

   ```text
   data/cv.csv
   data/job.csv
   data/matches.csv
   ```

4. Keep the CSVs local. They are excluded by `data/.gitignore`; do not force-add them to this public repository, especially if they contain identifiable resume text.
5. Inspect the headers and ensure candidate/job identifiers agree across files. The dataset schema may change; see `docs/DATA.md` and `scripts/README.md` for expected fields and aliases.

You may also use compatible reformatted CSVs from the course reference repository's `reformatted_data` directory. Do not copy a pre-trained evaluator or use precomputed component subscores as features: the project evaluates independent B0/B1/B2 text representations.

## File roles

- `cv.csv`: candidate identifier, resume/profile text, optionally structured skills.
- `job.csv`: job identifier, title, job description, optionally structured skills.
- `matches.csv`: recorded candidate/job identifiers and an overall compatibility score used only as proxy relevance.

Only recorded pairs are evaluated. Unrecorded pairs are unknown, not negative examples. Component subscores are not model inputs. The API's single-pair analysis works without dataset files; dataset ranking and offline evaluation require them.

Verify file presence without displaying any resume contents:

```bash
python -c "from pathlib import Path; print({n: (Path('data')/n).exists() for n in ['cv.csv','job.csv','matches.csv']})"
```
