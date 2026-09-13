from decimal import Decimal
from typing import List, Tuple
from datetime import date, timedelta

class ReferenceSimulator:
    """
    A brutally simple, unoptimized oracle simulator. 
    Prioritizes extreme mathematical clarity over performance.
    """
    @staticmethod
    def simulate_90_days(
        initial_balance: Decimal,
        minimum_balance: Decimal,
        request_date: date,
        events: List[dict],
        proposed_plan: List[Tuple[date, Decimal]] = None
    ) -> Tuple[bool, Decimal]:
        
        # End date is exactly 90 days after request_date
        end_date = request_date + timedelta(days=90)
        
        # Construct the complete timeline
        timeline_events = []
        for e in events:
            timeline_events.append((e["date"], e["amount"], e["description"]))
            
        if proposed_plan:
            for p_date, p_amount in proposed_plan:
                # Proposed payments are strictly outflows
                timeline_events.append((p_date, -abs(p_amount), "proposed_payment"))
                
        # To evaluate strictly, we step day by day
        current_date = request_date
        current_balance = initial_balance
        lowest_balance = current_balance
        
        is_safe = True
        
        while current_date <= end_date:
            # Find all events happening TODAY
            todays_events = [e for e in timeline_events if e[0] == current_date]
            
            # Intraday sorting: Inflows first, then standard outflows, then proposed payments
            todays_inflows = [e for e in todays_events if e[1] > 0]
            todays_outflows = [e for e in todays_events if e[1] <= 0 and e[2] != "proposed_payment"]
            todays_proposed = [e for e in todays_events if e[2] == "proposed_payment"]
            
            # Process inflows
            for _, amount, _ in todays_inflows:
                current_balance += amount
                
            # Process standard outflows
            for _, amount, _ in todays_outflows:
                current_balance += amount
                if current_balance < lowest_balance:
                    lowest_balance = current_balance
                if current_balance < minimum_balance:
                    is_safe = False
                    
            # Process proposed payments
            for _, amount, _ in todays_proposed:
                current_balance += amount
                if current_balance < lowest_balance:
                    lowest_balance = current_balance
                if current_balance < minimum_balance:
                    is_safe = False
                    
            current_date += timedelta(days=1)
            
        return is_safe, lowest_balance
