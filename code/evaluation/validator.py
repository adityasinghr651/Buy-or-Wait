import re

class DecisionValidator:
    def validate_decision(self, result: dict) -> dict:
        status = result["affordability_status"]
        method = result["recommended_payment_method"]
        plan = result["payment_plan"]
        earliest_date = result["earliest_date_for_full_payment"]
        
        # Rule: not_affordable invariant
        if status == "not_affordable":
            result["recommended_payment_method"] = "not_recommended"
            result["payment_plan"] = "none"
            result["amount_safe_to_pay"] = 0
            
        # Rule: affordable_later invariant
        if status == "affordable_later":
            if method != "wait":
                result["recommended_payment_method"] = "wait"
            if not earliest_date:
                # Fallback to not_affordable if we don't have a valid date
                result["affordability_status"] = "not_affordable"
                result["recommended_payment_method"] = "not_recommended"
                result["payment_plan"] = "none"
                result["amount_safe_to_pay"] = 0
                
        # Rule: Structural format for plans
        if method == "installments" or method == "partial_payment":
            if "|" not in plan and ":" not in plan:
                # Invalid plan string, fallback
                result["affordability_status"] = "not_affordable"
                result["recommended_payment_method"] = "not_recommended"
                result["payment_plan"] = "none"
                result["amount_safe_to_pay"] = 0
                
        # Rule: Safe amount bounds
        if float(result.get("amount_safe_to_pay", 0)) < 0:
            result["amount_safe_to_pay"] = 0
            
        # Rule: If method is wait, safe amount is usually the full amount on that date, 
        # but right now safe_amount means "amount safe to pay today". Wait, in the ground truth
        # sample_requests, for request_03 (wait), amount_safe_to_pay is 873000 (which is less than the requested amount 5491000).
        # Ah! `amount_safe_to_pay` is how much they could pay TODAY, even if the method is wait!
        # So we should not overwrite it.
        
        return result
