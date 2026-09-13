# Failure Clusters

Based on the row-level error matrix from `sample_requests.csv` (25 rows), there are 17 mismatched rows across 3 metrics. The errors can be grouped into the following distinct root-cause clusters:

## Cluster 1: Installment Plan Evaluation Failure
- **Affected Rows:** `request_02`, `request_12`
- **Symptom:** Predicted `not_affordable`, Expected `affordable_with_plan` (`installments`).
- **Hypothesis:** The optimizer fails to correctly evaluate installment plans. It might be simulating the full cost instead of the monthly installment, or rejecting the installment if the final payment goes beyond 90 days.

## Cluster 2: Off-By-One Date Boundaries
- **Affected Rows:** `request_18` (09-13 vs 09-15), `request_19` (09-14 vs 09-15), `request_23` (07-14 vs 07-15)
- **Symptom:** The `earliest_date_for_full_payment` is consistently 1-2 days earlier than expected.
- **Hypothesis:** The binary search in `engine.py` might be returning the day *before* an income event, whereas the ground truth requires the date of the income event itself, or there's an inequality (`<` vs `<=`) issue with balance checks on the event day.

## Cluster 3: False Affordability (Expenses Too Low)
- **Affected Rows:** `request_05`, `request_13`, `request_21`
- **Symptom:** Predicted `affordable_now`, Expected `not_affordable` or `affordable_with_plan` or `affordable_later`.
- **Hypothesis:** Some critical expenses are missing from the timeline, causing the balance to appear higher than it should. This is likely tied to the `1.5 * avg_gap` inactive rule still dropping slightly irregular expenses.

## Cluster 4: False Unaffordability (Expenses Too High)
- **Affected Rows:** `request_04`, `request_08`
- **Symptom:** Predicted `not_affordable`, Expected `affordable_later`. The system couldn't find ANY safe date in the next 90 days.
- **Hypothesis:** The `CashFlowSimulator` is over-projecting expenses for these users, keeping their balance perpetually below the required minimum + purchase amount, or we missed a pending income.

## Cluster 5: Optimizer Combinatorial Failure
- **Affected Rows:** `request_06`, `request_11`
- **Symptom:** Predicted `affordable_later`, Expected `affordable_with_plan`.
- **Hypothesis:** The optimizer couldn't find a valid set of spending reductions to make it safe today, likely because the total reductions required exceeded the sum of all stoppable/flexible events (which could trace back to Cluster 4 over-projection).

## Action Plan
We will attack **Cluster 2 (Off-By-One Date Boundaries)** and **Cluster 1 (Installment Plan Evaluation Failure)** first, as they are deterministic logic bugs rather than forecasting heuristics.
