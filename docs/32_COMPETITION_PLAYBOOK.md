# Competition Playbook

## 1. Core Paradigm: "AI Proposes. Code Proves."
Never rely on the LLM to make financial decisions, extrapolate dates, or calculate balances. The LLM's only job is to extract raw structured evidence from unstructured inputs (messages, images). The deterministic financial engine retains absolute authority.

## 2. Event Extrapolation
The engine's extrapolation algorithm uses a robust formula:
- Calculate `average_days_between` as `(last_date - first_date) // (occurrences - 1)`.
- Use a default of 30 days for single-occurrence events.
- **Critical Inactive Rule:** If the gap since the last occurrence exceeds `max(14, 1.5 * avg_gap)`, the event is marked as inactive and is NOT extrapolated. This prevents indefinite projection of stale "lifestyle" subscriptions.
- Ensure the very first projected occurrence is pushed into the timeline even if it mathematically lands just prior to the request date.

## 3. Combinatorial Payment Optimization
To synthesize `affordable_with_plan` or `affordable_later` statuses:
- Identify `flexible` or user-authorized stoppable/reducible events.
- Iterate through combinations of stops and reductions using `itertools`.
- Pass each synthetic timeline to the `CashFlowSimulator`.
- Select the plan that minimizes user disruption while strictly adhering to the absolute minimum balance.

## 4. Prompt Engineering for Financial Extraction
Ensure the AI system prompt enforces strict evidence-based extraction without speculative financial advice:
- Instruct the AI to assign a confidence score `[0.0 - 1.0]`.
- Drop any extracted entity with a confidence < `0.5`.
- Validate all facts semantically before merging them into the deterministic timeline.

## 5. Scoring & Iteration
Use the automated `scorer.py` against `sample_requests.csv` to validate all logic changes. A robust baseline of ~70% across all metrics indicates a highly generalized, non-overfit financial engine ready for evaluation.
