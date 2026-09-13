import sys
from pathlib import Path
import csv
from datetime import timedelta

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
from extraction.evidence import EvidenceValidator
from extraction.explainer import ExplanationAgent
from finance.engine import CashFlowSimulator
from finance.earliest_date import EarliestDateFinder
from optimization.planner import PaymentOptimizer
from finance.extrapolator import extrapolate_events
from evaluation.usage_tracker import UsageTracker
from evaluation.validator import DecisionValidator
from optimization.safe_amount import SafeAmountCalculator

def run_pipeline():
    print("Initializing components...")
    loader = DataLoader()
    loader.load_all(REQUESTS_FILE, PROFILES_FILE, OPTIONS_FILE, MESSAGES_FILE, EXCHANGE_RATES_FILE, EVENTS_FILE)
    
    converter = CurrencyConverter(loader.exchange_rates)
    sim = CashFlowSimulator()
    finder = EarliestDateFinder(sim)
    planner = PaymentOptimizer(sim, finder)
    safe_calc = SafeAmountCalculator(sim)
    explainer = ExplanationAgent()
    msg_agent = MessageExtractionAgent()
    img_agent = ImageExtractionAgent()
    evidence_validator = EvidenceValidator()
    usage_tracker = UsageTracker()
    decision_validator = DecisionValidator()
    
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
        
        # Load user events
        user_raw_events = [e for e in loader.events if e["user_id"] == req.user_id]
        
        # AI Extraction from messages
        user_messages = [m for m in loader.messages if m.user_id == req.user_id]
        extracted_facts = []
        willing_to_stop = set([x.lower() for x in profile.expense_categories_user_is_willing_to_stop])
        willing_to_reduce = set([x.lower() for x in profile.expense_categories_user_is_willing_to_reduce])
        
        for msg in user_messages:
            if msg.message_text:
                output = msg_agent.extract_facts(msg.message_text)
                valid_output = evidence_validator.validate(output)
                
                # Extract preferences
                for cat in valid_output.preferences.willing_to_stop:
                    willing_to_stop.add(cat.lower())
                for cat in valid_output.preferences.willing_to_reduce:
                    willing_to_reduce.add(cat.lower())
                    
                for f in valid_output.facts:
                    # Convert valid AI fact to timeline dict format
                    extracted_facts.append({
                        "event_id": f"ai_msg_{msg.message_id}",
                        "date": f.event_date if f.event_date else req.request_date,
                        "amount": f.amount if f.fact_type == "income" else -abs(f.amount),
                        "description": f.category,
                        "category": f.category,
                        "flexibility": "fixed",
                        "minimum_allowed_amount": "",
                        "is_extrapolated": False
                    })
                    print(f"DEBUG fact added: {extracted_facts[-1]}")
        
        # Inject AI facts into the raw events pool
        user_raw_events.extend(extracted_facts)
        
        # Extrapolate timeline
        events = extrapolate_events(user_raw_events, req.request_date)
        
        # Determine earliest safe date
        earliest_safe = finder.find_earliest_safe_date(
            profile.current_available_balance, profile.minimum_balance_to_keep,
            req.request_date, req.requested_amount, events
        )
        
        candidates = planner.evaluate_candidates(
            req, profile, options, events, earliest_safe,
            user_raw_events, willing_to_stop, willing_to_reduce
        )
        if req.request_id == 'request_11':
            print(f"DEBUG {req.request_id}: willing_to_stop={willing_to_stop}, willing_to_reduce={willing_to_reduce}")
            total = profile.current_available_balance - req.requested_amount
            print(f"INIT BALANCE AFTER PAY: {total}")
            for e in sorted(events, key=lambda x: x["date"]):
                if (e['date'] - req.request_date).days <= 30:
                    print(f"  {e['date']} {e['description']} {e['amount']}")
            if candidates:
                for c in candidates:
                    print(f"  Cand: {c.method} {c.spending_changes} is_safe={c.is_safe} lowest={c.lowest_balance}")
        best_plan = planner.rank_plans(candidates)
        
        # Always calculate the absolute safe amount today
        end_date = req.request_date + timedelta(days=90)
        absolute_safe_today = safe_calc.find_amount_safe_to_pay(
            profile.current_available_balance, profile.minimum_balance_to_keep,
            req.request_date, req.requested_amount, events, end_date
        )
        
        # Format output
        status = "not_affordable"
        method = "not_recommended"
        plan_str = "none"
        spending_changes = "none"
        safe_amount = float(absolute_safe_today)
        
        if best_plan:
            method = best_plan.method
            plan_str = best_plan.plan_string
            spending_changes = best_plan.spending_changes
            if method == "full_payment":
                status = "affordable_now"
                if spending_changes != "none":
                    status = "affordable_with_plan"
            elif method == "installments" or method == "partial_payment":
                status = "affordable_with_plan"
            elif method == "wait":
                status = "affordable_later"
                
        explanation = explainer.generate_explanation(
            req.requested_amount, profile.home_currency, status, best_plan, 
            profile.minimum_balance_to_keep, spending_changes
        )
        
        result = {
            "request_id": req_id,
            "amount_safe_to_pay": safe_amount,
            "affordability_status": status,
            "recommended_payment_method": method,
            "payment_plan": plan_str,
            "earliest_date_for_full_payment": earliest_safe.strftime('%Y-%m-%d') if earliest_safe else "",
            "spending_changes_needed": spending_changes,
            "decision_explanation": explanation
        }
        
        result = decision_validator.validate_decision(result)
        results.append(result)
        
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
    UsageTracker().generate_report()
    print("Orchestration complete!")
