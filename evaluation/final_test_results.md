# Final Test Results

## Command
```bash
python code/evaluation/test_*.py
```

## Output
```text
Running test_engine.py...
Running engine unit tests... All engine tests passed! 
Running test_extraction.py...
Testing extraction agents... Extraction agents tests passed! 
Running test_planner.py...
DEBUG planner: request_id=r1, allowed_methods=['full_payment', 'partial_payment'] Candidates: - wait: 2024-01-20:1000 (lowest bal: 1400) - partial_payment: 2024-01-01:900|2024-01-20:100 (lowest bal: 500) Best plan: partial_payment 
```

## Status
PASS
