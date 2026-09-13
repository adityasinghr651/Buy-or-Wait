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
        
        if status in ["scheduled", "pending"] and ev_date >= request_date:
            timeline.append(event_dict)
            
        if status == "settled" or ev_date < request_date or status in ["scheduled", "pending"]:
            grouped[desc].append(event_dict)
            
    # Extrapolate
    end_date = request_date + timedelta(days=90)
    
    for desc, history in grouped.items():
        history.sort(key=lambda x: x["date"])
        latest_event = history[-1]
        
        if len(history) <= 1 and not latest_event["event_id"].startswith("ai_msg_") and latest_event["date"] < request_date:
            if latest_event["amount"] > 0:
                continue
            
        if len(history) <= 1:
            avg_gap = 30
        else:
            total_days = (latest_event["date"] - history[0]["date"]).days
            avg_gap = max(1, total_days // (len(history) - 1))
            
        days_since_last = (request_date - latest_event["date"]).days
        # If the gap since the last occurrence is significantly larger than the average gap,
        # it is considered inactive/cancelled and should not be projected.
        # We use a 1.5x multiplier threshold, but minimum 14 days grace period for short gaps.
        if days_since_last > max(14, 1.5 * avg_gap):
            continue
            
        # Extrapolate until end_date
        if 28 <= avg_gap <= 31:
            days_of_month = set(x["date"].day for x in history)
            if len(days_of_month) == 1:
                from dateutil.relativedelta import relativedelta
                proj_date = latest_event["date"] + relativedelta(months=1)
                while proj_date <= end_date:
                    proj_event = latest_event.copy()
                    proj_event["date"] = proj_date
                    proj_event["is_extrapolated"] = True
                    timeline.append(proj_event)
                    proj_date += relativedelta(months=1)
                continue
                
        proj_date = latest_event["date"] + timedelta(days=avg_gap)
        
        while proj_date <= end_date:
            proj_event = latest_event.copy()
            proj_event["date"] = proj_date
            proj_event["is_extrapolated"] = True
            if desc == "Takeaway order": print(f"DEBUG: Extrapolating {desc} to {proj_date}")
            timeline.append(proj_event)
            proj_date += timedelta(days=avg_gap)
            
    return timeline
