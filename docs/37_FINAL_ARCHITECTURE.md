# 37 FINAL ARCHITECTURE

```text
                    REQUEST
                       │
                       ▼
                DATA INGESTION (CSV)
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
     STRUCTURED DATA          UNSTRUCTURED DATA
    (Events, Profile)         (Messages, Images)
          │                         │
          │                   ┌─────┴─────┐
          │                   ▼           ▼
          │                 LLM         VLM
          │                   │           │
          │                   └─────┬─────┘
          │                         ▼
          │                EVIDENCE VALIDATOR
          │                         │
          └──────────┬──────────────┘
                     ▼
              FINANCIAL STATE
              (Extrapolator)
                     │
                     ▼
            CASH FLOW SIMULATOR
                     │
                     ▼
             PAYMENT OPTIMIZER
                     │
                     ▼
             SAFETY VALIDATOR
                     │
                     ▼
               FINAL DECISION
                     │
                     ▼
                 output.csv
```

**Boundaries:**
- **AI Boundary:** LLM/VLM processing unstructured text/images.
- **Deterministic Boundary:** Extrapolator and Simulator.
- **Validation Boundary:** Safety Validator ensuring Minimum Balance is never breached.
