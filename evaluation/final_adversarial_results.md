# Adversarial Test Results

## Command
`python code/evaluation/adversarial_tests.py`

## Output
```text
Running Adversarial Test Suite...
DEBUG planner: request_id=rA, allowed_methods=['full_payment']
Test A Passed: Large obligations caught.
DEBUG planner: request_id=rD, allowed_methods=['full_payment', 'installments']
Test D Passed: Installment trap caught.
DEBUG planner: request_id=rG, allowed_methods=['full_payment']
Test G Passed: Minimum balance exactly matched is safe.
DEBUG planner: request_id=rH, allowed_methods=['full_payment']
Test H Passed: Future spending cuts don't fix immediate breaches.
All Adversarial Tests Passed!

```

## Status
PASS
