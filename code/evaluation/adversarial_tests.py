import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

CODE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CODE_DIR))

from models.state import UserRequest, FinancialProfile, PaymentOption
from finance.engine import CashFlowSimulator
from finance.earliest_date import EarliestDateFinder
from optimization.planner import PaymentOptimizer

def run_adversarial_tests():
    sim = CashFlowSimulator()
    finder = EarliestDateFinder(sim)
    planner = PaymentOptimizer(sim, finder)
    
    print("Running Adversarial Test Suite...")
    
    # ---------------------------------------------------------
    # Test A: Large Balance / Large Obligations
    # High balance, but a huge rent payment tomorrow.
    # ---------------------------------------------------------
    req_a = UserRequest("rA", "uA", date(2024, 1, 1), "purchase", Decimal("4000"), date(2024, 1, 10), True, "")
    prof_a = FinancialProfile("uA", "USD", Decimal("5000"), Decimal("500"), [], [], [], [], ["full_payment"], None)
    events_a = [{"date": date(2024, 1, 2), "amount": Decimal("-4500"), "description": "rent", "event_id": "", "category": "", "flexibility": "fixed", "minimum_allowed_amount": ""}]
    
    # 5000 - 4000 = 1000. Next day: 1000 - 4500 = -3500 (Fail!)
    # Should not be safe.
    candidates = planner.evaluate_candidates(req_a, prof_a, [], events_a, None)
    assert len(candidates) == 0, "Test A Failed: Should have rejected due to future obligation."
    print("Test A Passed: Large obligations caught.")
    
    # ---------------------------------------------------------
    # Test D: Installment Trap
    # Purchase unaffordable in full, but affordable with installments
    # ---------------------------------------------------------
    req_d = UserRequest("rD", "uD", date(2024, 1, 1), "purchase", Decimal("3000"), date(2024, 3, 1), False, "")
    prof_d = FinancialProfile("uD", "USD", Decimal("1500"), Decimal("500"), [], [], [], [], ["full_payment", "installments"], None)
    opt_d = PaymentOption("opt1", "rD", "installments", Decimal("1050"), 3, date(2024, 1, 1), 30, Decimal("150"), Decimal("3150"))
    
    # User only has 1500 (min 500, so 1000 buffer). Full payment (3000) fails.
    # Installment is 1050 today. 1500 - 1050 = 450 < 500 (Fail!)
    # Wait, the installment is 1050, so buffer is 450, which breaches minimum 500!
    # So installment should ALSO fail!
    events_d = [{"date": date(2024, 1, 15), "amount": Decimal("2000"), "description": "income", "event_id": "", "category": "", "flexibility": "fixed", "minimum_allowed_amount": ""}]
    
    candidates = planner.evaluate_candidates(req_d, prof_d, [opt_d], events_d, None)
    assert len(candidates) == 0, "Test D Failed: Installment breached minimum balance."
    print("Test D Passed: Installment trap caught.")
    
    # ---------------------------------------------------------
    # Test G: Minimum Balance Trap
    # Purchase leaves exactly minimum balance. Should be safe!
    # ---------------------------------------------------------
    req_g = UserRequest("rG", "uG", date(2024, 1, 1), "purchase", Decimal("1000"), date(2024, 1, 10), False, "")
    prof_g = FinancialProfile("uG", "USD", Decimal("2000"), Decimal("1000"), [], [], [], [], ["full_payment"], None)
    candidates = planner.evaluate_candidates(req_g, prof_g, [], [], None)
    assert len(candidates) == 1, "Test G Failed: Exact minimum balance is safe."
    print("Test G Passed: Minimum balance exactly matched is safe.")

    # ---------------------------------------------------------
    # Test H: Essential Expense Trap (Requires Spending Changes)
    # ---------------------------------------------------------
    req_h = UserRequest("rH", "uH", date(2024, 1, 1), "purchase", Decimal("500"), date(2024, 1, 10), False, "")
    prof_h = FinancialProfile("uH", "USD", Decimal("1000"), Decimal("200"), [], [], ["entertainment"], ["subscriptions"], ["full_payment"], None)
    # Rent is essential, cannot be cut. Subscription is stoppable.
    events_h = [
        {"date": date(2024, 1, 2), "amount": Decimal("-400"), "description": "rent", "event_id": "", "category": "", "flexibility": "fixed", "minimum_allowed_amount": ""},
        {"date": date(2024, 1, 3), "amount": Decimal("-100"), "description": "subscriptions", "event_id": "", "category": "", "flexibility": "fixed", "minimum_allowed_amount": ""}
    ]
    # Without changes: 1000 - 500 (purchase) = 500. Rent: 500 - 400 = 100.
    # 100 is < 200 (minimum). Fails!
    # If we stop subscription, does it help?
    # Wait, if purchase is on Jan 1, rent on Jan 2 drops it to 100. 100 < 200.
    # Stopping a subscription on Jan 3 DOES NOT rescue the minimum balance drop on Jan 2!
    # This is a very subtle trap.
    candidates = planner.evaluate_candidates(req_h, prof_h, [], events_h, None)
    assert len(candidates) == 0, "Test H Failed: Stopping future expense doesn't fix past breach."
    print("Test H Passed: Future spending cuts don't fix immediate breaches.")

    print("All Adversarial Tests Passed!")

if __name__ == "__main__":
    run_adversarial_tests()
