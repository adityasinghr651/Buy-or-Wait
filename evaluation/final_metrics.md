# Final Metrics

## Command
`python code/evaluation/scorer.py`

## Output
```text
Running pipeline on sample_requests.csv...
Initializing components...
Loaded 25 requests. Processing...
DEBUG planner: request_id=request_01, allowed_methods=['full_payment']
DEBUG planner: request_id=request_02, allowed_methods=['partial_payment', 'installments']
DEBUG planner: request_id=request_03, allowed_methods=['full_payment', 'partial_payment', 'installments']
DEBUG planner: request_id=request_04, allowed_methods=['full_payment']
DEBUG planner: request_id=request_05, allowed_methods=['full_payment', 'partial_payment', 'installments']
DEBUG planner: request_id=request_06, allowed_methods=['full_payment', 'partial_payment']
DEBUG planner: request_id=request_07, allowed_methods=['installments']
DEBUG planner: request_id=request_08, allowed_methods=['full_payment']
DEBUG planner: request_id=request_09, allowed_methods=['full_payment', 'partial_payment', 'installments']
DEBUG planner: request_id=request_10, allowed_methods=['partial_payment', 'installments']
DEBUG planner: request_id=request_11, allowed_methods=['full_payment']
DEBUG request_11: willing_to_stop={'cloud_storage'}, willing_to_reduce={'dining', 'entertainment'}
INIT BALANCE AFTER PAY: 50421795
  2025-05-05 Home association fee -2954500
  2025-05-08 Municipal utilities -2796165.18
  2025-05-08 Bulk pantry shop -1590529.64
  2025-05-09 Vehicle insurance premium -1881000
  2025-05-10 Child education fee -2544100
  2025-05-11 Ride-hailing trip -1122838.73
  2025-05-12 Regular medicine purchase -2826901.92
  2025-05-14 Cloud storage plan -168150
  2025-05-15 Base salary 23256000
  2025-05-16 Games and recreation -1674887.61
  2025-05-24 Monthly sales commission 8502888.2
  Cand: full_payment none is_safe=True lowest=34537609.53
  Cand: wait none is_safe=True lowest=34537609.53
DEBUG planner: request_id=request_12, allowed_methods=['partial_payment', 'installments']
DEBUG planner: request_id=request_13, allowed_methods=['full_payment']
DEBUG planner: request_id=request_14, allowed_methods=['partial_payment']
DEBUG planner: request_id=request_15, allowed_methods=['partial_payment']
DEBUG planner: request_id=request_16, allowed_methods=['full_payment', 'installments']
DEBUG planner: request_id=request_17, allowed_methods=['installments']
DEBUG planner: request_id=request_18, allowed_methods=['full_payment', 'partial_payment']
DEBUG planner: request_id=request_19, allowed_methods=['partial_payment', 'installments']
DEBUG planner: request_id=request_20, allowed_methods=['full_payment', 'partial_payment', 'installments']
DEBUG planner: request_id=request_21, allowed_methods=['full_payment']
DEBUG planner: request_id=request_22, allowed_methods=['installments']
DEBUG planner: request_id=request_23, allowed_methods=['full_payment', 'partial_payment', 'installments']
DEBUG planner: request_id=request_24, allowed_methods=['partial_payment']
DEBUG planner: request_id=request_25, allowed_methods=['full_payment', 'installments']
Writing 25 predictions to C:\Users\adity\Documents\Hackerank\evaluation\sample_output.csv
[request_01] Mismatch in affordability_status: Expected 'affordable_now', Got 'not_affordable'
[request_01] Mismatch in recommended_payment_method: Expected 'full_payment', Got 'not_recommended'
[request_01] Mismatch in earliest_date_for_full_payment: Expected '2024-03-03', Got ''
[request_03] Mismatch in earliest_date_for_full_payment: Expected '2019-11-15', Got '2019-10-15'
[request_06] Mismatch in affordability_status: Expected 'affordable_with_plan', Got 'not_affordable'
[request_06] Mismatch in recommended_payment_method: Expected 'full_payment', Got 'not_recommended'
[request_07] Mismatch in earliest_date_for_full_payment: Expected '2024-10-23', Got '2024-10-15'
[request_08] Mismatch in affordability_status: Expected 'affordable_later', Got 'not_affordable'
[request_08] Mismatch in recommended_payment_method: Expected 'wait', Got 'not_recommended'
[request_08] Mismatch in earliest_date_for_full_payment: Expected '2025-04-15', Got ''
[request_10] Mismatch in earliest_date_for_full_payment: Expected '', Got '2024-12-06'
[request_11] Mismatch in affordability_status: Expected 'affordable_with_plan', Got 'affordable_now'
[request_11] Mismatch in earliest_date_for_full_payment: Expected '2025-07-15', Got '2025-05-03'
[request_13] Mismatch in affordability_status: Expected 'affordable_later', Got 'affordable_now'
[request_13] Mismatch in recommended_payment_method: Expected 'wait', Got 'full_payment'
[request_13] Mismatch in earliest_date_for_full_payment: Expected '2024-05-15', Got '2024-03-07'
[request_18] Mismatch in earliest_date_for_full_payment: Expected '2026-09-15', Got '2026-08-15'
[request_21] Mismatch in affordability_status: Expected 'affordable_with_plan', Got 'affordable_now'
[request_21] Mismatch in earliest_date_for_full_payment: Expected '2026-04-15', Got '2026-04-03'
[request_22] Mismatch in earliest_date_for_full_payment: Expected '2025-01-15', Got '2024-12-15'

=== SCORING REPORT (Against sample_requests.csv) ===
affordability_status: 19/25 (76.0%)
recommended_payment_method: 21/25 (84.0%)
earliest_date_for_full_payment: 15/25 (60.0%)

```

## Status
PASS
