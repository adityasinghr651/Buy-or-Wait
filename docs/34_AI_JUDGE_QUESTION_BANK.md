# 34 AI JUDGE QUESTION BANK & ANSWER KEY

## Basic Questions
1. **What is the goal of this project?**
   *Short Answer:* To evaluate if a user can safely afford a large purchase over a 90-day window without violating a minimum balance constraint, factoring in their historical recurring events and unstructured financial context (like chat messages or images).
   *Technical Answer:* The system integrates structured CSV data with AI-extracted facts to run a deterministic 90-day cash-flow simulation. It evaluates combinatorial payment plans (full, installments, partial) to find the one with minimal disruption that satisfies `projected_balance >= minimum_allowed_amount`.
   *Relevant Component:* `main.py`, `CashFlowSimulator`
   *Metric:* Passes 250 requests processed successfully.

2. **How do you handle unstructured data?**
   *Short Answer:* We use Gemini LLM/VLM to extract entities.
   *Technical Answer:* Unstructured messages and images are passed to Gemini with a strict JSON schema prompt to extract dates, amounts, and intent, alongside a confidence score. This structured output is validated before entering the deterministic pipeline.
   *Relevant Component:* `ai/gemini_provider.py`

3. **What is the format of the output?**
   *Short Answer:* A CSV file.
   *Technical Answer:* A standard CSV file `output.csv` with `request_id, affordability_status, recommended_payment_method, earliest_date_for_full_payment, explanation`.

## Intermediate Questions
4. **Why is the system divided into AI and Deterministic components?**
   *Short Answer:* "AI Proposes. Code Proves."
   *Technical Answer:* LLMs are notoriously unreliable at arithmetic and date constraints. By confining the LLM to an extraction/understanding role (proposing facts), the Python engine handles the math (proving safety), ensuring reproducibility and strict constraint adherence.
   *Relevant Component:* Architecture separation between `ai/` and `finance/engine.py`.

5. **How does the extrapolator work?**
   *Short Answer:* It calculates average gaps between historical events.
   *Technical Answer:* It groups historical events, calculates `avg_gap = total_days // (occurrences - 1)`, and projects them forward. A Critical Inactive Rule drops chains if the gap since the last occurrence exceeds `max(14, 1.5 * avg_gap)`.
   *Relevant Component:* `finance/extrapolator.py`

6. **What is the optimization logic?**
   *Short Answer:* It ranks safe plans to minimize user disruption.
   *Technical Answer:* The Payment Optimizer uses `itertools` to generate candidate plans (stopping stoppable expenses, reducing reducible expenses). It simulates them, discards unsafe ones, and ranks the survivors by prioritizing plans that require the least behavioral changes (e.g., no stops > no reductions).
   *Relevant Component:* `optimization/planner.py`

## Advanced Questions
7. **How do you handle AI hallucinations?**
   *Short Answer:* Confidence thresholds and semantic validation.
   *Technical Answer:* The LLM returns a confidence score. Facts with `< 0.5` are rejected. The `EvidenceValidator` also ensures extracted amounts mathematically align with the context and dates are within valid bounds.

8. **How do you avoid overfitting?**
   *Short Answer:* Generalized rules instead of hardcoded exceptions.
   *Technical Answer:* We strictly prohibited `if request_id == ...`. Every mismatch in the evaluation led to generalized financial logic fixes, such as the 1.5x gap breaking rule or the conservative single-occurrence salary handling.

9. **What if the LLM API goes down?**
   *Short Answer:* Deterministic fallback.
   *Technical Answer:* The system falls back to using only the structured CSV data. The `CashFlowSimulator` still runs safely, albeit lacking the unstructured context, leading to a conservative decision.

## Attack Questions
10. **Why should I trust your recurrence detector?**
    *Answer:* Because it employs a robust moving average and a strict 1.5x gap threshold to immediately prune stale "lifestyle" subscriptions, preventing infinite forecasting of obsolete expenses.
11. **What if your LLM lies?**
    *Answer:* The LLM only extracts evidence. If it extracts a wrong number, the `EvidenceValidator` schema checking and deterministic conflict resolution (e.g. conservative bias) mitigate the impact. The LLM cannot override the deterministic math.
12. **Why 90 days?**
    *Answer:* It balances short-term liquidity safety with the computational bounds of the simulation, aligning with typical consumer credit risk horizons.
