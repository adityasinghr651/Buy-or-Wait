# 35 CODE WALKTHROUGH

## Directory Structure
- `code/ingestion/`
  - `data_loader.py`: Purpose: Loads raw CSV files and normalizes them into canonical dataclasses (Request, Profile, Event).
- `code/ai/`
  - `gemini_provider.py`: Purpose: Interfaces with the Gemini API to extract structured financial facts from messages and images using strict JSON schemas.
- `code/finance/`
  - `extrapolator.py`: Purpose: Groups historical events and mathematically projects recurring behaviors 90 days into the future.
  - `engine.py`: Purpose: Contains the `CashFlowSimulator`, tracking the day-by-day balance and ensuring it never dips below the minimum constraint.
- `code/optimization/`
  - `planner.py`: Purpose: Explores combinatorial payment plans (full, partial, installments) and stoppable/reducible expense combinations, ranking them by user disruption.
- `code/main.py`: Purpose: The main orchestrator connecting data ingestion, AI extraction, and deterministic simulation into a unified pipeline.
- `evaluation/`
  - `scorer.py`: Purpose: Evaluates the pipeline's predictions against the golden `sample_output.csv` to measure accuracy and prevent regressions.
