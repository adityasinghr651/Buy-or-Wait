from decimal import Decimal
from typing import List, Tuple
from datetime import date
from finance.engine import CashFlowSimulator

class SafeAmountCalculator:
    def __init__(self, simulator: CashFlowSimulator):
        self.simulator = simulator

    def find_amount_safe_to_pay(
        self,
        current_balance: Decimal,
        minimum_balance: Decimal,
        request_date: date,
        requested_amount: Decimal,
        events: List[Tuple[date, Decimal, str]],
        end_date: date
    ) -> Decimal:
        """
        Calculates the maximum amount that can be safely paid on `request_date`.
        Returns a Decimal between 0 and requested_amount.
        """
        # First check if the full requested amount is safe
        is_safe, _, _, _ = self.simulator.simulate(
            current_balance, minimum_balance, request_date, end_date, events,
            [(request_date, requested_amount)]
        )
        if is_safe:
            return requested_amount
            
        # If not safe, find the bottleneck in the simulation without any payment
        is_safe, lowest, fail_date, _ = self.simulator.simulate(
            current_balance, minimum_balance, request_date, end_date, events, []
        )
        
        if not is_safe:
            # If it's already unsafe without making ANY payment, we can't pay anything
            return Decimal("0.0")
            
        # The amount safe to pay is the difference between the lowest projected balance
        # and the minimum balance.
        # Example: Lowest projected balance = 1800, Min balance = 1000
        # Then we can safely pay 800 on day 1, and the lowest point will perfectly hit 1000.
        safe_buffer = lowest - minimum_balance
        
        if safe_buffer < Decimal("0.0"):
            return Decimal("0.0")
            
        return min(safe_buffer, requested_amount)
