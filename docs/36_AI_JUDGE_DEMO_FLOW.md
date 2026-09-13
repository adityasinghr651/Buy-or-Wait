# 36 AI JUDGE DEMO FLOW

1. **Show Problem:** Introduce a user wanting to buy a laptop, but they have a minimum balance constraint and unstructured messages indicating a salary delay.
2. **Show Dataset:** Briefly display `historical_events.csv` and the natural language message.
3. **Show Architecture:** Display the "AI Proposes. Code Proves." diagram.
4. **Show Extraction:** Demonstrate how the LLM extracts `{"date": "...", "amount": "...", "confidence": 0.95}` from the message.
5. **Show Validation:** Show the Evidence Validator merging this fact into the deterministic timeline.
6. **Show Financial State:** Display the 90-day extrapolated timeline.
7. **Show Simulation:** Demonstrate the `CashFlowSimulator` calculating the day-by-day balance.
8. **Show Optimization:** Show candidate plans. Point out how a "wait" plan is selected because the "full_payment" plan violates the minimum balance constraint on day 14.
9. **Show Final Output:** Display the final output CSV with the structured decision and explanation.
