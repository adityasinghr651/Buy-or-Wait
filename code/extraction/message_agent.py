import json
import logging
from typing import Dict, Any, List, Optional
from datetime import date
from models.state import Message

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT_TEMPLATE = """
You are a strict financial data extraction agent. 
Read the following message and extract any financial updates into a structured JSON format.

RULES:
1. ONLY extract information if it relates to a financial event (salary, rent, expenses, bonuses, refunds).
2. If the message says an amount is "pending", "expected", "might", or "not approved", set "is_confirmed" to false.
3. If the message confirms an amount and a date, set "is_confirmed" to true.
4. Output MUST be a valid JSON array of objects.

JSON SCHEMA for each object in the array:
{{
  "fact_type": "income_update" | "expense_update" | "cancellation" | "other",
  "amount": <float or null>,
  "currency": "<3 letter code or null>",
  "effective_date": "YYYY-MM-DD" or null,
  "is_confirmed": <boolean>,
  "related_event_id": "<ID or null>"
}}

MESSAGE CONTENT:
{message_text}
"""

class MessageExtractionAgent:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        
    def _call_llm(self, prompt: str) -> str:
        """
        Mockable LLM call. In production, this connects to Gemini, OpenAI, etc.
        """
        if self.llm_client:
            # Replace with actual SDK call, e.g. self.llm_client.generate_content(prompt)
            raise NotImplementedError("LLM client execution not implemented.")
            
        # Mock behavior for testing based on known sample messages
        if "gaji bulanan Anda naik menjadi IDR 42750000" in prompt:
            return '[{"fact_type": "income_update", "amount": 42750000, "currency": "IDR", "effective_date": "2025-08-15", "is_confirmed": true, "related_event_id": "EMP-0001"}]'
        elif "Bonus kuartalan Anda masih menunggu hasil akhir" in prompt:
            return '[{"fact_type": "income_update", "amount": null, "currency": null, "effective_date": null, "is_confirmed": false, "related_event_id": "EMP-0003"}]'
        
        return "[]"

    def process_message(self, message: Message) -> List[Dict[str, Any]]:
        prompt = EXTRACTION_PROMPT_TEMPLATE.format(message_text=message.message_text)
        
        try:
            raw_response = self._call_llm(prompt)
            # Basic cleanup in case LLM wraps response in ```json ... ```
            clean_response = raw_response.strip().removeprefix("```json").removesuffix("```").strip()
            
            facts = json.loads(clean_response)
            if not isinstance(facts, list):
                logger.warning(f"Message {message.message_id} extraction did not return a list.")
                return []
                
            # If the message record already contained a related_event_id, enforce it
            for fact in facts:
                if message.related_event_id and not fact.get("related_event_id"):
                    fact["related_event_id"] = message.related_event_id
                    
            return facts
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from LLM for message {message.message_id}")
            return []
        except Exception as e:
            logger.error(f"Error extracting message {message.message_id}: {e}")
            return []
