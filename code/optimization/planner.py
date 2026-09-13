from decimal import Decimal
from typing import List, Tuple, Dict, Any
from datetime import date
from models.state import FinancialProfile, PaymentOption, UserRequest
from finance.engine import CashFlowSimulator
from finance.earliest_date import EarliestDateFinder

from optimization.safe_amount import SafeAmountCalculator
from datetime import timedelta

class CandidatePlan:
    def __init__(self, method: str, plan_string: str, total_cost: Decimal, 
                 start_date: date, num_payments: int, option_id: str = "", end_date: date = None):
        self.method = method
        self.plan_string = plan_string
        self.total_cost = total_cost
        self.start_date = start_date
        self.end_date = end_date or start_date
        self.num_payments = num_payments
        self.option_id = option_id
        
        self.is_safe = False
        self.lowest_balance = Decimal("0.0")
        self.spending_changes = "none"

class PaymentOptimizer:
    def __init__(self, simulator: CashFlowSimulator, earliest_finder: EarliestDateFinder):
        self.simulator = simulator
        self.earliest_finder = earliest_finder
        self.safe_amount_calc = SafeAmountCalculator(simulator)

    def evaluate_candidates(
        self,
        request: UserRequest,
        profile: FinancialProfile,
        payment_options: List[PaymentOption],
        events: List[Dict[str, Any]],
        earliest_safe_date: date,
        user_raw_events: List[Dict[str, Any]] = None,
        willing_to_stop: set = None,
        willing_to_reduce: set = None
    ) -> List[CandidatePlan]:
        candidates = []
        end_date = request.request_date + timedelta(days=90)
        allowed_methods = profile.payment_methods_user_will_consider
        
        willing_to_stop = willing_to_stop or set()
        willing_to_reduce = willing_to_reduce or set()
        
        # Identify flexible events the user is willing to change
        stoppable_events = []
        reducible_events = []
        if user_raw_events:
            for ev in user_raw_events:
                cat = ev.get("category", "").lower()
                # Also allow based on dataset flexibility field if not explicitly overridden
                flex = ev.get("flexibility", "")
                
                is_stop = (cat in willing_to_stop) or ("all" in willing_to_stop) or (flex == "stoppable")
                is_reduce = (cat in willing_to_reduce) or ("all" in willing_to_reduce) or (flex == "reducible")
                
                if is_stop:
                    stoppable_events.append(ev)
                if is_reduce and not is_stop:
                    reducible_events.append(ev)
        
        # 1. Full Payment
        if "full_payment" in allowed_methods:
            plan_str = f"{request.request_date}:{request.requested_amount}"
            c = CandidatePlan("full_payment", plan_str, request.requested_amount, 
                              request.request_date, 1, end_date=request.request_date)
            
            is_safe, lowest, _, _ = self.simulator.simulate(
                profile.current_available_balance, profile.minimum_balance_to_keep,
                request.request_date, end_date, events, 
                [(request.request_date, request.requested_amount)]
            )
            c.is_safe = is_safe
            c.lowest_balance = lowest
            
            if not c.is_safe and (stoppable_events or reducible_events):
                # Calculate the exact shortfall to determine how much to reduce
                shortfall = profile.minimum_balance_to_keep - c.lowest_balance
                
                # Attempt to stop an event to make it safe
                for sev in stoppable_events:
                    # Rerun simulation with spending change
                    is_safe_mod, lowest_mod, _, _ = self.simulator.simulate(
                        profile.current_available_balance, profile.minimum_balance_to_keep,
                        request.request_date, end_date, events, 
                        [(request.request_date, request.requested_amount)],
                        spending_changes=[f"stop:{sev['event_id']}"]
                    )
                    if is_safe_mod:
                        c.is_safe = True
                        c.lowest_balance = lowest_mod
                        c.spending_changes = f"stop:{sev['event_id']}"
                        break
                        
                # If still not safe, try reducing events
                if not c.is_safe:
                    for rev in reducible_events:
                        rev_amount = abs(float(rev["amount"]))
                        # Reduce by exactly the shortfall, but cap at the total event amount
                        reduction_needed = min(float(shortfall), rev_amount)
                        # Actually wait, if the shortfall is because of a single occurrence, 
                        # reducing the event by `shortfall` means the new amount is `rev_amount - shortfall`.
                        if reduction_needed > 0:
                            new_amount = rev_amount - reduction_needed
                            is_safe_mod, lowest_mod, _, _ = self.simulator.simulate(
                                profile.current_available_balance, profile.minimum_balance_to_keep,
                                request.request_date, end_date, events, 
                                [(request.request_date, request.requested_amount)],
                                spending_changes=[f"reduce_to:{rev['event_id']}:{new_amount:.2f}"]
                            )
                            if is_safe_mod:
                                c.is_safe = True
                                c.lowest_balance = lowest_mod
                                # Format as specified: reduce:event_id:by:amount
                                c.spending_changes = f"reduce:{rev['event_id']}:by:{reduction_needed:.2f}"
                                if request.user_id == "user_06":
                                    print(f"[DEBUG] user_06 found safe plan by reducing {rev['event_id']} by {reduction_needed:.2f}")
                                break
                            else:
                                if request.user_id == "user_06":
                                    print(f"[DEBUG] user_06 still unsafe after reducing {rev['event_id']} by {reduction_needed:.2f} (lowest_mod={lowest_mod})")
                        
            candidates.append(c)

        # 2. Wait
        if "wait" in allowed_methods or "full_payment" in allowed_methods:
            if earliest_safe_date and earliest_safe_date <= request.desired_completion_date:
                plan_str = f"{earliest_safe_date}:{request.requested_amount}"
                c = CandidatePlan("wait", plan_str, request.requested_amount, earliest_safe_date, 1, end_date=earliest_safe_date)
                
                is_safe, lowest, _, _ = self.simulator.simulate(
                    profile.current_available_balance, profile.minimum_balance_to_keep,
                    request.request_date, end_date, events, 
                    [(earliest_safe_date, request.requested_amount)]
                )
                c.is_safe = is_safe
                c.lowest_balance = lowest
                candidates.append(c)
                
        # 3. Installments
        if "installments" in allowed_methods:
            for opt in payment_options:
                if opt.payment_method != "installments":
                    continue
                if profile.max_installment_months and (opt.number_of_payments > profile.max_installment_months):
                    continue
                
                schedule = []
                current_date = opt.first_payment_date
                plan_parts = []
                for _ in range(opt.number_of_payments):
                    schedule.append((current_date, opt.payment_amount))
                    plan_parts.append(f"{current_date}:{opt.payment_amount}")
                    current_date += timedelta(days=opt.payment_frequency_days)
                
                plan_str = "|".join(plan_parts)
                final_date = schedule[-1][0]
                
                if final_date > request.desired_completion_date:
                    continue
                    
                c = CandidatePlan("installments", plan_str, opt.total_payable_amount, 
                                  opt.first_payment_date, opt.number_of_payments, opt.payment_option_id, end_date=final_date)
                
                is_safe, lowest, _, _ = self.simulator.simulate(
                    profile.current_available_balance, profile.minimum_balance_to_keep,
                    request.request_date, end_date, events, schedule
                )
                c.is_safe = is_safe
                c.lowest_balance = lowest
                candidates.append(c)
                
        # 4. Partial Payment
        if "partial_payment" in allowed_methods and request.allows_partial_payment:
            if earliest_safe_date and earliest_safe_date <= request.desired_completion_date:
                amount_safe = self.safe_amount_calc.find_amount_safe_to_pay(
                    profile.current_available_balance, profile.minimum_balance_to_keep,
                    request.request_date, request.requested_amount, events, end_date
                )
                
                if Decimal("0") < amount_safe < request.requested_amount:
                    remainder = request.requested_amount - amount_safe
                    plan_str = f"{request.request_date}:{amount_safe}|{earliest_safe_date}:{remainder}"
                    
                    c = CandidatePlan("partial_payment", plan_str, request.requested_amount, 
                                      request.request_date, 2, end_date=earliest_safe_date)
                    
                    schedule = [(request.request_date, amount_safe), (earliest_safe_date, remainder)]
                    is_safe, lowest, _, _ = self.simulator.simulate(
                        profile.current_available_balance, profile.minimum_balance_to_keep,
                        request.request_date, end_date, events, schedule
                    )
                    c.is_safe = is_safe
                    c.lowest_balance = lowest
                    candidates.append(c)
                
        return [c for c in candidates if c.is_safe]
        
    def rank_plans(self, safe_candidates: List[CandidatePlan]) -> CandidatePlan:
        if not safe_candidates:
            return None
            
        def sort_key(c: CandidatePlan):
            # 1. Complete by desired_completion_date (Already filtered/assumed)
            # 2. No spending changes (All these are without spending changes currently)
            has_changes = 1 if c.spending_changes != "none" else 0
            # 3. Minimize total amount paid
            # 4. Start payment earlier
            # 5. Use fewer payments
            # 6. Lowest payment_option_id
            return (
                has_changes,
                c.total_cost,
                c.start_date,
                c.num_payments,
                c.option_id
            )
            
        safe_candidates.sort(key=sort_key)
        return safe_candidates[0]
