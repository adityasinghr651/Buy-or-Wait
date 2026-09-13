# Phase 3: AI Orchestration & Integration Report

## Executive Summary
We successfully integrated a provider-agnostic AI Extraction layer into the financial pipeline. The core architectural rule—"AI Proposes. Code Proves"—was strictly adhered to. The AI models solely extract structured factual evidence from unstructured data sources, while the deterministic financial engine retains absolute authority over cash-flow simulation, limit validation, and the final decision.

## AI Provider Abstraction
We implemented a robust abstraction (`code/ai/base.py`) that insulates the financial pipeline from any specific SDK.
- **Provider Chosen:** A flexible factory pattern supports `google-genai` by default, securely parsing the `AI_API_KEY` from the environment.
- **Mock Fallback:** We introduced `MockProvider`, returning empty Pydantic schemas, which allows the pipeline to execute deterministically without network access.

## Extraction Agents
1. **MessageAgent:** Uses a strictly versioned prompt (`prompts/message_extraction_v1.txt`) to extract income/expense facts, explicit user preferences, certainty, and confidence scores from natural text.
2. **ImageAgent:** Implements VLM integration with a parallel prompt focusing on visible financial receipts and invoices. (Note: The specific `images.csv` data source was missing from the provided dataset but the architecture fully supports it.)

## Evidence Layer & Semantic Validation
Extracted facts flow through the `EvidenceValidator` (`code/extraction/evidence.py`).
- Low-confidence outputs (<0.5) are automatically stripped.
- Domain rules (e.g., negative magnitudes) are normalized or rejected.
- Validated evidence is converted into canonical event dictionaries and merged directly into the deterministic timeline prior to the `CashFlowSimulator`.

## Caching & Token Usage
To minimize costs and increase reproducibility, we implemented:
- **`AICache`**: Deterministically caches responses using a SHA-256 hash of the model name and prompt string.
- **`UsageTracker`**: Logs `input_tokens`, `output_tokens`, and estimated costs to `usage_log.csv`.
- An initial run against the dataset generated `evaluation/usage_report.md`.

## Decision Invariant Tests
Following integration, we re-ran the full suite of Phase 2 tests (`adversarial_tests.py`, `fuzz_tests.py`).
**Results:** Zero regressions. The deterministic engine correctly processed the timeline, including mock AI facts, without violating any minimum-balance or temporal invariants.

## Prompt Injection Defense
Both prompt versions explicitly instruct the model to treat user messages and images as untrusted data, specifically prohibiting the execution of "ignore previous instructions" anomalies.

## Next Steps
The architecture is now fully ready for Phase 4. We can safely swap the provider to the production API key, benchmark `gemini-2.5-pro` against the evaluation suite, and finalize the combinatorial flexible spending reduction loops.
