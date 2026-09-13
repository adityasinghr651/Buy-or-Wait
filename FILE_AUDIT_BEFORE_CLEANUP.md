# File Audit Before Final Cleanup

## KEEP
- `code/` (Core application logic)
- `dataset/` (Challenge data)
- `docs/ARCHITECTURE.md`, `CODE_WALKTHROUGH.md`, `AI_JUDGE_GUIDE.md`, `EVALUATION.md` (Consolidated documentation)
- `tests/` (if separated, but ours are in `code/evaluation/`)
- `README.md`
- `output.csv`
- `.gitignore`

## SUBMISSION-REQUIRED
- `code.zip`
- `evaluation/usage_report.md`
- `log.txt` (if exists)

## DELETE
- `__pycache__` and `*.pyc` (Temporary python artifacts)
- `evaluation/phase6_completion.json`, `phase6_completion.md` (Temporary tracking matrices)
- `evaluation/usage_log.csv` (Temporary data dump)
- `evaluation/failure_clusters.md`, `metric_verification.md` (Intermediate dev documents)
- `FINAL_RELEASE_STATUS.md`, `FINAL_REPOSITORY_AUDIT.md`, `FINAL_REPOSITORY_STRUCTURE.md` (Previous artifacts, replaced by this cleanup)

## MOVE/ARCHIVE
- N/A

## DEVELOPMENT-ONLY
- All removed intermediate dumps
