import sys
from pathlib import Path
import csv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import (
    REQUESTS_FILE, PROFILES_FILE, OPTIONS_FILE,
    MESSAGES_FILE, EXCHANGE_RATES_FILE, EVENTS_FILE, OUTPUT_FILE
)
from ingestion.data_loader import DataLoader
from utils.currency import CurrencyConverter
from extraction.message_agent import MessageExtractionAgent
from extraction.image_agent import ImageExtractionAgent
from extraction.explainer import ExplanationAgent
from finance.engine import CashFlowSimulator
from finance.earliest_date import EarliestDateFinder
from optimization.planner import PaymentOptimizer
from finance.extrapolator import extrapolate_events

def run_pipeline():
    print("Initializing components...")
    loader = DataLoader()
    loader.load_all(REQUESTS_FILE, PROFILES_FILE, OPTIONS_FILE, MESSAGES_FILE, EXCHANGE_RATES_FILE, EVENTS_FILE)
    
    converter = CurrencyConverter(loader.exchange_rates)
    sim = CashFlowSimulator()
    finder = EarliestDateFinder(sim)
    planner = PaymentOptimizer(sim, finder)
    explainer = ExplanationAgent()
    msg_agent = MessageExtractionAgent()
    
    print(f"Loaded {len(loader.requests)} requests. Processing...")
    
    results = []
    
    for req_id, req in loader.requests.items():
        profile = loader.profiles.get(req.user_id)
        if not profile:
            # Fallback for missing profile
            results.append({
                "request_id": req_id, "amount_safe_to_pay": 0, "affordability_status": "not_affordable",
                "recommended_payment_method": "not_recommended", "payment_plan": "none",
                "earliest_date_for_full_payment": "", "spending_changes_needed": "none",
                "decision_explanation": "Missing user financial profile."
            })
            continue
            
        options = loader.payment_options.get(req_id, [])
        
        # Load user events and extrapolate timeline
        user_raw_events = [e for e in loader.events if e["user_id"] == req.user_id]
        events = extrapolate_events(user_raw_events, req.request_date)
        
        # Determine earliest safe date
        earliest_safe = finder.find_earliest_safe_date(
            profile.current_available_balance, profile.minimum_balance_to_keep,
            req.request_date, req.requested_amount, events
        )
        
        candidates = planner.evaluate_candidates(req, profile, options, events, earliest_safe)
        best_plan = planner.rank_plans(candidates)
        
        # Format output
        status = "not_affordable"
        method = "not_recommended"
        plan_str = "none"
        spending_changes = "none"
        safe_amount = 0
        
        if best_plan:
            method = best_plan.method
            plan_str = best_plan.plan_string
            if method == "full_payment":
                status = "affordable_now"
                safe_amount = req.requested_amount
            elif method == "installments" or method == "partial_payment":
                status = "affordable_with_plan"
                if method == "partial_payment":
                    # Parse first payment amount
                    safe_amount = float(plan_str.split("|")[0].split(":")[1])
            elif method == "wait":
                status = "affordable_later"
                
        explanation = explainer.generate_explanation(
            req.requested_amount, profile.home_currency, status, best_plan, 
            profile.minimum_balance_to_keep, spending_changes
        )
        
        results.append({
            "request_id": req_id,
            "amount_safe_to_pay": safe_amount,
            "affordability_status": status,
            "recommended_payment_method": method,
            "payment_plan": plan_str,
            "earliest_date_for_full_payment": earliest_safe.strftime('%Y-%m-%d') if earliest_safe else "",
            "spending_changes_needed": spending_changes,
            "decision_explanation": explanation
        })
        
    print(f"Writing {len(results)} predictions to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "request_id", "amount_safe_to_pay", "affordability_status", 
            "recommended_payment_method", "payment_plan", 
            "earliest_date_for_full_payment", "spending_changes_needed", 
            "decision_explanation"
        ])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    run_pipeline()
    print("Orchestration complete!")
