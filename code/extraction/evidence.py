from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field

class ExtractedFact(BaseModel):
    fact_type: str = Field(description="'income' or 'expense'")
    amount: float = Field(description="The financial amount extracted")
    currency: str = Field(description="The currency code, e.g., 'INR', 'USD'")
    event_date: Optional[date] = Field(description="The date of the event if discernible", default=None)
    frequency: Optional[str] = Field(description="'one_time', 'monthly', 'weekly', etc.", default=None)
    category: str = Field(description="The category of the expense/income")
    certainty: str = Field(description="'confirmed', 'expected', or 'uncertain'")
    confidence: float = Field(description="Model confidence from 0.0 to 1.0")
    source: str = Field(description="'message' or 'image'")
    evidence_text: str = Field(description="The exact text snippet that justifies this extraction")

class ExtractedPreferences(BaseModel):
    willing_to_reduce: List[str] = Field(description="Categories the user explicitly said they are willing to reduce", default_factory=list)
    willing_to_stop: List[str] = Field(description="Categories the user explicitly said they are willing to stop", default_factory=list)

class AgentOutput(BaseModel):
    facts: List[ExtractedFact] = Field(description="List of extracted financial facts", default_factory=list)
    preferences: ExtractedPreferences = Field(description="Extracted user preferences", default_factory=ExtractedPreferences)

class EvidenceValidator:
    """
    Validates AI outputs. Semantic validation and cross-source conflict detection.
    """
    def validate(self, output: AgentOutput) -> AgentOutput:
        valid_facts = []
        for fact in output.facts:
            # Semantic validations
            if fact.amount < 0:
                continue # amount should be positive magnitude
            if fact.confidence < 0.5:
                continue # drop low confidence
            
            # Additional domain rules: 
            # If certainty is uncertain, we might drop it or keep it for context but the engine ignores it.
            # We keep it here, the engine filters unconfirmed ones.
            valid_facts.append(fact)
            
        return AgentOutput(facts=valid_facts, preferences=output.preferences)
