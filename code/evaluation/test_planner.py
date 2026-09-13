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

def test_planner():
    sim = CashFlowSimulator()
    finder = EarliestDateFinder(sim)
    planner = PaymentOptimizer(sim, finder)
    
    req = UserRequest(
        request_id="r1", user_id="u1", request_date=date(2024, 1, 1), 
        request_type="purchase", requested_amount=Decimal("1000"),
        desired_completion_date=date(2024, 2, 1),
        allows_partial_payment=True, request_text=""
    )
    
    prof = FinancialProfile(
        user_id="u1", home_currency="USD", current_available_balance=Decimal("2000"),
        minimum_balance_to_keep=Decimal("500"), financial_priorities=[],
        expense_categories_to_protect=[], expense_categories_user_is_willing_to_reduce=[],
        expense_categories_user_is_willing_to_stop=[],
        payment_methods_user_will_consider=["full_payment", "partial_payment"],
        max_installment_months=None
    )
    
    events = [
        {"date": date(2024, 1, 15), "amount": Decimal("-600"), "description": "rent", "event_id": "", "category": "", "flexibility": "fixed", "minimum_allowed_amount": ""}
    ]
    
    # 1000 payment on Jan 1:
    # Jan 1: 2000 - 1000 = 1000 (>= 500)
    # Jan 15: 1000 - 600 = 400 (< 500) -> FAIL full_payment
    
    # Partial payment: safe amount on Jan 1
    # 2000 (start) - 600 (rent) = 1400 (lowest without payment)
    # 1400 - 500 (min) = 900 safe to pay
    
    # Earliest safe date for full 1000: No income is coming, so it's never safe in 90 days
    # Wait, if no income comes, full payment is never safe. 
    # Let's add income on Jan 20
    events.append({"date": date(2024, 1, 20), "amount": Decimal("1000"), "description": "salary", "event_id": "", "category": "", "flexibility": "fixed", "minimum_allowed_amount": ""})
    
    # Earliest full payment date: Jan 20
    earliest = finder.find_earliest_safe_date(
        prof.current_available_balance, prof.minimum_balance_to_keep,
        req.request_date, req.requested_amount, events
    )
    
    candidates = planner.evaluate_candidates(req, prof, [], events, earliest)
    print("Candidates:")
    for c in candidates:
        print(f"- {c.method}: {c.plan_string} (lowest bal: {c.lowest_balance})")
        
    best = planner.rank_plans(candidates)
    if best:
        print(f"Best plan: {best.method}")
    else:
        print("No safe plans found.")

if __name__ == "__main__":
    test_planner()
