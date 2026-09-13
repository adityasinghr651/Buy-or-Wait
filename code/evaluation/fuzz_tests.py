import sys
from pathlib import Path
import random
from decimal import Decimal
from datetime import date, timedelta

CODE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CODE_DIR))

from finance.engine import CashFlowSimulator
from evaluation.reference_simulator import ReferenceSimulator

def generate_random_scenario():
    initial_balance = Decimal(str(random.randint(1000, 100000)))
    minimum_balance = Decimal(str(random.randint(0, 5000)))
    
    start_date = date(2024, 1, 1)
    
    # Generate random events
    num_events = random.randint(0, 50)
    events = []
    for _ in range(num_events):
        offset = random.randint(0, 89)
        ev_date = start_date + timedelta(days=offset)
        amount = Decimal(str(random.randint(-5000, 5000)))
        # Make sure no zeroes to avoid confusion
        if amount == 0:
            amount = Decimal("100")
        desc = "income" if amount > 0 else "expense"
        events.append({
            "event_id": f"e_{_}",
            "date": ev_date,
            "amount": amount,
            "description": desc,
            "category": "test",
            "flexibility": "fixed",
            "minimum_allowed_amount": ""
        })
        
    # Generate random proposed plan
    num_payments = random.randint(1, 3)
    proposed_plan = []
    for _ in range(num_payments):
        offset = random.randint(0, 89)
        p_date = start_date + timedelta(days=offset)
        p_amount = Decimal(str(random.randint(100, 2000)))
        proposed_plan.append((p_date, p_amount))
        
    return initial_balance, minimum_balance, start_date, events, proposed_plan

def run_fuzz_tests(iterations=1000):
    prod_sim = CashFlowSimulator()
    ref_sim = ReferenceSimulator()
    
    failures = 0
    
    print(f"Running {iterations} fuzz tests...")
    
    for i in range(iterations):
        initial, minimum, start, events, plan = generate_random_scenario()
        end_date = start + timedelta(days=90)
        
        prod_safe, prod_lowest, _, _ = prod_sim.simulate(
            initial, minimum, start, end_date, events, plan
        )
        
        ref_safe, ref_lowest = ref_sim.simulate_90_days(
            initial, minimum, start, events, plan
        )
        
        if prod_safe != ref_safe or (prod_safe and prod_lowest != ref_lowest):
            print(f"FAILED on iteration {i}")
            print(f"Initial: {initial}, Min: {minimum}")
            print(f"Prod: safe={prod_safe}, lowest={prod_lowest}")
            print(f"Ref: safe={ref_safe}, lowest={ref_lowest}")
            print("Events:")
            for e in sorted(events, key=lambda x: x[0]): print(" ", e)
            print("Plan:")
            for p in sorted(plan, key=lambda x: x[0]): print(" ", p)
            failures += 1
            break
            
    if failures == 0:
        print("All fuzz tests passed! Production engine mathematically identical to Reference oracle.")
    else:
        print("Fuzz testing failed.")
        sys.exit(1)

if __name__ == "__main__":
    run_fuzz_tests()
