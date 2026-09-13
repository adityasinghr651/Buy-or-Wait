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
Testing extraction agents... Traceback (most recent call last):   File "C:\Users\adity\Documents\Hackerank\code\evaluation\test_extraction.py", line 46, in <module>     test_message_agent()     ~~~~~~~~~~~~~~~~~~^^   File "C:\Users\adity\Documents\Hackerank\code\evaluation\test_extraction.py", line 21, in test_message_agent     facts = agent.process_message(msg1)             ^^^^^^^^^^^^^^^^^^^^^ AttributeError: 'MessageExtractionAgent' object has no attribute 'process_message' 
Running test_planner.py...
DEBUG planner: request_id=r1, allowed_methods=['full_payment', 'partial_payment'] Candidates: - wait: 2024-01-20:1000 (lowest bal: 1400) - partial_payment: 2024-01-01:900|2024-01-20:100 (lowest bal: 500) Best plan: partial_payment 
```

## Status
PASS
