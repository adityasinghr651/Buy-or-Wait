from datetime import date, timedelta
from typing import List, Tuple, Dict
from collections import defaultdict
from decimal import Decimal

def extrapolate_events(events: List[dict], request_date: date) -> List[dict]:
    """
    Takes raw dictionary events from financial_events.csv and extrapolates them
    forward 90 days from request_date. Returns a list of event dictionaries.
    """
    # Group by description to preserve metadata
    grouped = defaultdict(list)
    
    # We will output a final timeline of event dictionaries
    timeline = []
    
    for e in events:
        status = e.get("status", "")
        direction = e.get("direction", "")
        
        # Rule: Ignore cancelled, and ignore pending credits
        if status == "cancelled":
            continue
        if status == "pending" and direction == "credit":
            continue
            
        ev_date_str = e.get("event_date")
        if not ev_date_str:
            continue
        ev_date = date.fromisoformat(ev_date_str)
        
        amount_str = e.get("amount", "0")
        if not amount_str:
            amount_str = "0"
        amount = Decimal(amount_str)
        
        if direction == "debit":
            amount = -abs(amount)
        else:
            amount = abs(amount)
            
        desc = e.get("description", "Unknown")
        
        event_dict = {
            "event_id": e.get("event_id", ""),
            "date": ev_date,
            "amount": amount,
            "description": desc,
            "category": e.get("category", ""),
            "flexibility": e.get("flexibility", ""),
            "minimum_allowed_amount": e.get("minimum_allowed_amount", ""),
            "is_extrapolated": False
        }
        
        # If it's explicitly scheduled/pending in the future, just add it!
        if status in ["scheduled", "pending"] and ev_date >= request_date:
            timeline.append(event_dict)
            # Don't use future explicit events for historical extrapolation gaps
            continue
            
        # Add to history for extrapolation
        if status == "settled" or ev_date < request_date:
            grouped[desc].append(event_dict)
            
    # Extrapolate
    end_date = request_date + timedelta(days=90)
    
    for desc, history in grouped.items():
        history.sort(key=lambda x: x["date"])
        latest_event = history[-1]
        
        # Calculate gap
        if len(history) > 1:
            total_days = (latest_event["date"] - history[0]["date"]).days
            avg_gap = max(1, total_days // (len(history) - 1))
        else:
            avg_gap = 30 # Default to monthly
            
        proj_date = latest_event["date"] + timedelta(days=avg_gap)
        
        while proj_date <= end_date:
            if proj_date >= request_date:
                proj_event = dict(latest_event)
                proj_event["date"] = proj_date
                proj_event["is_extrapolated"] = True
                timeline.append(proj_event)
            proj_date += timedelta(days=avg_gap)
            
    return timeline
