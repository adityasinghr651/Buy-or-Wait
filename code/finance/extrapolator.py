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
            
    # Build set of (date, amount) pairs already covered by scheduled/pending credits
    # to avoid double-counting salary when Next confirmed salary is scheduled
    # Also find the EARLIEST scheduled credit date — we stop extrapolating recurring credits beyond it
    end_date = request_date + timedelta(days=90)
    scheduled_credit_dates = set()
    earliest_scheduled_credit = None
    for e in timeline:
        if e["amount"] > 0 and not e["is_extrapolated"]:
            scheduled_credit_dates.add(e["date"])
            if earliest_scheduled_credit is None or e["date"] < earliest_scheduled_credit:
                earliest_scheduled_credit = e["date"]
            
    for desc, history in grouped.items():
        history.sort(key=lambda x: x["date"])
        latest_event = history[-1]
        
        if len(history) <= 1 and not latest_event["event_id"].startswith("ai_msg_") and latest_event["date"] < request_date:
            # Skip all single-occurrence past events — no frequency pattern to extrapolate reliably
            continue
            
        if len(history) <= 1 and not latest_event["event_id"].startswith("ai_msg_") and latest_event["date"] >= request_date:
            # Single-occurrence future scheduled/pending events (e.g. 'Next confirmed salary')
            # are one-time confirmations — do NOT extrapolate them further
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
            
        if 28 <= avg_gap <= 31:
            days_of_month = set(x["date"].day for x in history)
            if len(days_of_month) == 1:
                from dateutil.relativedelta import relativedelta
                proj_date = latest_event["date"] + relativedelta(months=1)
                # pyrefly: ignore [unknown-name]
                while proj_date <= end_date:
                    # Skip if a scheduled credit already covers this specific date
                    if latest_event["amount"] > 0 and proj_date in scheduled_credit_dates:
                        proj_date += relativedelta(months=1)
                        continue
                    proj_event = latest_event.copy()
                    proj_event["date"] = proj_date
                    proj_event["is_extrapolated"] = True
                    timeline.append(proj_event)
                    proj_date += relativedelta(months=1)
                continue
                
        proj_date = latest_event["date"] + timedelta(days=avg_gap)
        
        # pyrefly: ignore [unknown-name]
        while proj_date <= end_date:
            # Skip if a scheduled credit already covers this specific date (avoid double-counting)
            if latest_event["amount"] > 0 and proj_date in scheduled_credit_dates:
                proj_date += timedelta(days=avg_gap)
                continue
            proj_event = latest_event.copy()
            proj_event["date"] = proj_date
            proj_event["is_extrapolated"] = True
            timeline.append(proj_event)
            proj_date += timedelta(days=avg_gap)
            
    return timeline
