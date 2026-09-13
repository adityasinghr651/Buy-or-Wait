import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

CODE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CODE_DIR))

from finance.engine import CashFlowSimulator
from finance.earliest_date import EarliestDateFinder

def test_engine_safe_payment():
    sim = CashFlowSimulator()
    events = [
        {"date": date(2024, 1, 15), "amount": Decimal("500"), "description": "income", "event_id": "", "category": "", "flexibility": "fixed", "minimum_allowed_amount": ""},
        {"date": date(2024, 1, 20), "amount": Decimal("-200"), "description": "rent", "event_id": "", "category": "", "flexibility": "fixed", "minimum_allowed_amount": ""}
    ]
    # Current balance 1000, minimum 500, request date Jan 1
    # We want to pay 700 on Jan 1
    # 1000 - 700 = 300 < 500 (breach minimum)
    
    is_safe, lowest, fail_date, reason = sim.simulate(
        initial_balance=Decimal("1000"),
        minimum_balance=Decimal("500"),
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31),
        events=events,
        proposed_plan=[(date(2024, 1, 1), Decimal("700"))]
    )
    assert not is_safe, "Should not be safe because balance drops to 300 on Jan 1"
    assert lowest == Decimal("300")
    assert fail_date == date(2024, 1, 1)

def test_earliest_safe_date():
    sim = CashFlowSimulator()
    finder = EarliestDateFinder(sim)
    
    events = [
        {"date": date(2024, 1, 15), "amount": Decimal("500"), "description": "income", "event_id": "", "category": "", "flexibility": "fixed", "minimum_allowed_amount": ""},
        {"date": date(2024, 1, 20), "amount": Decimal("-200"), "description": "rent", "event_id": "", "category": "", "flexibility": "fixed", "minimum_allowed_amount": ""}
    ]
    # Starting balance 1000, min 500, request 700
    # Jan 1: Balance = 1000. 1000 - 700 = 300 < 500 (Fail)
    # Jan 15: Balance = 1000 + 500 = 1500. 1500 - 700 = 800 >= 500 (Pass!)
    
    earliest = finder.find_earliest_safe_date(
        current_balance=Decimal("1000"),
        minimum_balance=Decimal("500"),
        request_date=date(2024, 1, 1),
        request_amount=Decimal("700"),
        events=events
    )
    assert earliest == date(2024, 1, 15), f"Expected Jan 15, got {earliest}"

if __name__ == "__main__":
    print("Running engine unit tests...")
    test_engine_safe_payment()
    test_earliest_safe_date()
    print("All engine tests passed!")
