from decimal import Decimal
from typing import List, Tuple
from datetime import date, timedelta
from finance.engine import CashFlowSimulator

class EarliestDateFinder:
    def __init__(self, simulator: CashFlowSimulator):
        self.simulator = simulator

    def find_earliest_safe_date(
        self,
        current_balance: Decimal,
        minimum_balance: Decimal,
        request_date: date,
        request_amount: Decimal,
        events: List[Tuple[date, Decimal, str]]
    ) -> date:
        """
        Finds the earliest date on which a single full payment of `request_amount`
        can be made without breaching the minimum balance within the 90-day window.
        """
        end_date = request_date + timedelta(days=90)
        
        test_date = request_date
        while test_date <= end_date:
            proposed_plan = [(test_date, request_amount)]
            
            is_safe, lowest, _, _ = self.simulator.simulate(
                initial_balance=current_balance,
                minimum_balance=minimum_balance,
                start_date=request_date,
                end_date=end_date,
                events=events,
                proposed_plan=proposed_plan
            )
            
            if is_safe:
                return test_date
                
            test_date += timedelta(days=1)
            
        return None  # No safe date found in the 90-day window
