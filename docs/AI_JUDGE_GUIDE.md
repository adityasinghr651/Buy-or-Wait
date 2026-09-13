# 33 AI JUDGE MASTER GUIDE

## Overview
This document serves as the primary technical defense for the AI Judge interview.

## 1. Problem
The problem is to determine if a user can safely afford a large purchase using cash flow forecasting over a 90-day window. The system must account for current balance, future obligations, minimum balance constraints, and unstructured financial context (natural language messages and images).

## 2. Requirements
- Forecast cash flow for 90 days.
- Ensure the account balance never drops below a minimum threshold.
- Extract financial context from unstructured inputs.
- Synthesize candidate payment plans (full, partial, installments, wait).
- Recommend the plan that minimizes user disruption while strictly adhering to safety constraints.

## 3. Architecture
The architecture follows a strict "AI Proposes. Code Proves." paradigm.
- **Data Ingestion:** Loads CSVs, messages, and images.
- **AI/VLM Extraction:** Extracts structured evidence (dates, amounts) from unstructured inputs.
- **Evidence Validator:** Validates extracted facts for schema correctness and confidence.
- **Financial State Builder:** Merges deterministic history with validated AI facts.
- **Cash Flow Simulator:** Extrapolates recurring events and simulates daily balances.
- **Payment Optimizer:** Generates and ranks candidate payment plans.
- **Safety Validator:** Evaluates plans against the minimum balance constraint.
- **Decision Engine:** Selects the best plan and formulates an explanation.

## 4. Data
The system processes structured CSV data (historical events, profile, catalog) and unstructured data (messages, images).

## 5. AI
We use an LLM (Gemini) to extract structured financial facts from messages and images. The LLM is strictly confined to an extraction role; it does not make financial decisions or calculate safety constraints.

## 6. Financial Engine
The deterministic financial engine is the ultimate authority. It extrapolates recurring events based on average gaps and strictly simulates cash flow day-by-day.

## 7. Optimization
The Payment Optimizer tests combinatorial plans (modifying stoppable/reducible expenses and payment methods) against the Cash Flow Simulator. It ranks safe plans to minimize disruption.

## 8. Validation
Safety is validated by ensuring that under a given plan, the simulated balance NEVER drops below `minimum_allowed_amount` throughout the 90-day window.

## 9. Evaluation
The system was iteratively evaluated against a dataset of requests. Failure clusters (e.g., date truncation, chain-breaking logic) were identified and resolved through generalized fixes, ensuring no overfitting to specific users or requests.

## 10. Final Output
The system outputs a CSV containing affordability status, recommended payment method, earliest safe date, and an explanation for each request.
