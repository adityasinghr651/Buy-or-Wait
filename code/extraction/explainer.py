import logging
from optimization.planner import CandidatePlan

logger = logging.getLogger(__name__)

EXPLANATION_PROMPT = """
You are a financial agent. Draft a 1-2 sentence explanation of the following decision.
Do not invent any numbers. Rely strictly on the following data:

Requested Amount: {req_amount}
Requested Currency: {currency}
Decision Status: {status}
Chosen Plan: {plan_str}
Lowest Projected Balance: {lowest_bal}
Minimum Required Balance: {min_bal}
Spending Changes Needed: {spending_changes}

EXAMPLE OUTPUTS:
- Pay ZAR 25,256 today. This leaves at least ZAR 18,000 available over the next 90 days.
- Use 3 installments of IDR 15,952,906.67, starting 8 August 2025. This leaves at least IDR 29,158,400 available.
- Wait until 15 June 2024, then pay IDR 12,693,000 in full. Paying sooner would put the IDR 30,686,600 minimum at risk.
- Do not make this payment by 10 February 2025. None of the available options keeps the INR 225,400 minimum protected.
- Stop the family streaming plan, then pay EUR 620.40 today. This leaves at least EUR 800 available.
"""

class ExplanationAgent:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        
    def generate_explanation(self, req_amount, currency, status, plan, min_bal, spending_changes) -> str:
        # For a hackathon where LLM calls are expensive, we can use a deterministic fallback or template first.
        # Template-based deterministic generation matching exactly the examples:
        if status == "not_affordable":
            return f"Do not proceed with the {currency} {req_amount:,.2f} request. None of the available options keeps the {currency} {min_bal:,.2f} minimum protected."
            
        if not plan:
            return ""
            
        lowest = plan.lowest_balance
        if plan.method == "full_payment":
            if spending_changes and spending_changes != "none":
                return f"Make the required spending changes, then pay {currency} {req_amount:,.2f} today. This leaves at least {currency} {lowest:,.2f} available."
            return f"Pay {currency} {req_amount:,.2f} today. This leaves at least {currency} {lowest:,.2f} available over the next 90 days."
            
        elif plan.method == "wait":
            return f"Wait until {plan.start_date.strftime('%d %B %Y')}, then pay {currency} {req_amount:,.2f} in full. Paying earlier would put the {currency} {min_bal:,.2f} minimum at risk."
            
        elif plan.method == "installments":
            return f"Use {plan.num_payments} installments, starting {plan.start_date.strftime('%d %B %Y')}. This leaves at least {currency} {lowest:,.2f} available."
            
        elif plan.method == "partial_payment":
            return f"Pay the safe amount today and the remainder on {plan.end_date.strftime('%d %B %Y')}. This completes the full request and keeps the {currency} {min_bal:,.2f} minimum protected."
            
        return "Explanation could not be generated."
