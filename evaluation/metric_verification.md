# Metric Verification

## How the 64% and 68% metrics were calculated:
- **Denominator:** Exactly 25 rows from `sample_requests.csv`.
- **Ground Truth:** `sample_requests.csv` includes official ground truth columns appended to the request inputs (e.g., `affordability_status`, `recommended_payment_method`, `earliest_date_for_full_payment`, etc.).
- **Comparison:** The `code/evaluation/scorer.py` performs an exact string match (stripped of whitespace) between the generated `evaluation/sample_output.csv` and the ground truth in `sample_requests.csv`.
- **Fields Compared:** Only 3 fields are currently scored:
  - `affordability_status` (64%)
  - `recommended_payment_method` (68%)
  - `earliest_date_for_full_payment` (32%)
- **Fields Ignored in Scoring:** `amount_safe_to_pay`, `payment_plan`, `spending_changes_needed`, `decision_explanation`.
- **Official vs Proxy:** This is a **LOCAL PROXY — NOT OFFICIAL HACKATHON SCORE**. The official score will likely run against a hidden dataset (`requests.csv`) and evaluate all output columns.

## Wrong Rows (Based on Phase 4 Baseline)
- **Affordability Status Mismatches (9/25 errors):** requests 02, 04, 05, 06, 08, 11, 12, 13, 21.
- **Recommended Payment Method Mismatches (8/25 errors):** requests 02, 04, 05, 06, 08, 11, 12, 13.
- **Earliest Date Mismatches (17/25 errors):** requests 02, 03, 04, 05, 06, 07, 08, 10, 11, 12, 13, 18, 19, 21, 22, 23, 24.
