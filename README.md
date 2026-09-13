# Buy or Wait?

## Problem
In the modern financial landscape, individuals frequently face the dilemma of whether to make a purchase now using an installment plan or to wait until they have sufficient funds. The challenge is complex because it involves synthesizing rigid, structured financial data (like historical transactions and account balances) with ambiguous, unstructured context (like human language messages and invoice images). 

## Solution
This repository presents a hybrid engine designed to tackle the "Buy or Wait?" challenge. It extracts facts from unstructured messages using AI and processes them through a deterministic cash-flow simulator to guarantee absolute financial safety.

## Architecture
The system is cleanly divided into two primary subsystems:
1. **Unstructured Extraction:** A Large Language Model (LLM) and Vision-Language Model (VLM) ingest messages and images, parse intentions (e.g., job losses, upcoming bonuses, or new debts), and emit structured factual events.
2. **Deterministic Evaluation:** A rigid Cash Flow Simulator extrapolates future balances based on historical trends. It integrates the AI-extracted facts and simulates candidate payment plans across a timeline, rigorously checking against a Minimum Balance threshold.

## Why AI?
Code cannot natively read a user saying "I am losing my job next month" or understand an attached invoice image. The AI's purpose is strictly confined to perception and extraction—bridging the gap between human context and our strict data model.

## Why deterministic financial logic?
AI is probabilistic and prone to hallucination; it cannot be trusted to perform exact arithmetic or guarantee a safety constraint over a 60-day cash flow simulation. The deterministic engine guarantees that the final decision mathematically satisfies the safety invariants. *AI proposes, Code proves.*

## Data Flow
```text
UNSTRUCTURED INPUT
       ↓
      AI (Extraction)
       ↓
STRUCTURED EVIDENCE
       ↓
DETERMINISTIC FINANCIAL ENGINE (Extrapolator & Simulator)
       ↓
SAFETY VALIDATION
       ↓
FINAL OUTPUT (output.csv)
```

## Project Structure
- `code/ai/`: Language model integration and unstructured data extraction.
- `code/finance/`: Deterministic cash flow engine and date math.
- `code/optimization/`: Payment plan search algorithms.
- `dataset/`: Required input CSVs.
- `docs/`: Technical and architectural documentation.
- `evaluation/`: Output metrics and testing artifacts.

## How to Run
Ensure `dataset/` contains all the required files, then execute the pipeline:
```bash
python code/main.py
```

## Output Format
The pipeline produces an `output.csv` with the required schema:
`request_id`, `amount_safe_to_pay`, `affordability_status`, `recommended_payment_method`, `payment_plan`, `earliest_date_for_full_payment`, `spending_changes_needed`, `decision_explanation`

## Safety Guarantees
- The engine guarantees the `lowest_balance` never falls below the `minimum_balance_to_keep`.
- Unsafe plans are never recommended, even if the AI hallucinates a favorable outcome.

## Evaluation
See `docs/EVALUATION.md` and `evaluation/usage_report.md` for full breakdown of final pipeline metrics, output schema audits, and token usage constraints.
