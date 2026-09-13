from decimal import Decimal
from typing import List, Tuple, Optional
from datetime import date, timedelta

class CashFlowSimulator:
    def __init__(self):
        pass

    def simulate(
        self,
        initial_balance: Decimal,
        minimum_balance: Decimal,
        start_date: date,
        end_date: date,
        events: List[dict],
        proposed_plan: List[Tuple[date, Decimal]] = None,
        spending_changes: List[str] = None
    ) -> Tuple[bool, Decimal, Optional[date], Optional[str]]:
        """
        Simulate cash flow over a given period.
        
        :param initial_balance: User's available balance on start_date
        :param minimum_balance: The minimum balance to maintain
        :param start_date: Evaluation date (request_date)
        :param end_date: 90 days from request_date
        :param events: List of confirmed event dicts
        :param proposed_plan: List of (date, amount) payments proposed for the request
        :return: (is_safe, lowest_balance, failure_date, failure_reason)
        """
        balance = initial_balance
        lowest_balance = balance
        
        # Process events based on spending changes
        stops = set()
        reductions = {}
        if spending_changes:
            for sc in spending_changes:
                parts = sc.split(":")
                if parts[0] == "stop":
                    stops.add(parts[1])
                elif parts[0] == "reduce_to":
                    reductions[parts[1]] = Decimal(parts[2])
                    
        timeline = []
        for e in events:
            # e is a dict
            eid = e.get("event_id")
            if eid in stops:
                continue
                
            amount = e["amount"]
            if eid in reductions:
                # amount is negative. reductions are positive magnitudes.
                amount = -abs(reductions[eid])
                
            timeline.append((e["date"], amount, e["description"]))
            
        # Add proposed plan as an explicit event
        if proposed_plan:
            for p_date, p_amount in proposed_plan:
                # Payments are outflows, so they should be negative
                timeline.append((p_date, -abs(p_amount), "proposed_payment"))
                
        # Priority logic for same-day events:
        # 0: Inflows (amount > 0)
        # 1: Standard Outflows (amount <= 0, description != 'proposed_payment')
        # 2: Proposed Payment (amount <= 0, description == 'proposed_payment')
        def get_priority(amount, description):
            if amount > 0:
                return 0
            if description == "proposed_payment":
                return 2
            return 1
            
        timeline.sort(key=lambda x: (x[0], get_priority(x[1], x[2])))
        
        for event_date, amount, description in timeline:
            if event_date < start_date:
                # In a real scenario, past events shouldn't be in the future timeline,
                # but if they are, they are already accounted for in current_balance
                continue
                
            if event_date > end_date:
                break
                
            balance += amount
            
            if balance < lowest_balance:
                lowest_balance = balance
                
            if balance < minimum_balance:
                return False, lowest_balance, event_date, f"Balance dropped below minimum ({minimum_balance}) due to {description}"
                
        return True, lowest_balance, None, None
