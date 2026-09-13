from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date
from decimal import Decimal

@dataclass
class UserRequest:
    request_id: str
    user_id: str
    request_date: date
    request_type: str
    requested_amount: Decimal
    desired_completion_date: date
    allows_partial_payment: bool
    request_text: str

@dataclass
class FinancialProfile:
    user_id: str
    home_currency: str
    current_available_balance: Decimal
    minimum_balance_to_keep: Decimal
    financial_priorities: List[str]
    expense_categories_to_protect: List[str]
    expense_categories_user_is_willing_to_reduce: List[str]
    expense_categories_user_is_willing_to_stop: List[str]
    payment_methods_user_will_consider: List[str]
    max_installment_months: Optional[int]

@dataclass
class PaymentOption:
    payment_option_id: str
    request_id: str
    payment_method: str
    payment_amount: Decimal
    number_of_payments: int
    first_payment_date: date
    payment_frequency_days: int
    financing_fee: Decimal
    total_payable_amount: Decimal

@dataclass
class Message:
    message_id: str
    user_id: str
    request_id: Optional[str]
    related_event_id: Optional[str]
    sent_at: str # Keeping as ISO string for now
    source_type: str
    message_text: str

@dataclass
class ExchangeRate:
    rate_date: date
    from_currency: str
    to_currency: str
    rate: Decimal

# Since financial_events.csv and images.csv are missing, we define provisional classes for them
@dataclass
class FinancialEvent:
    event_id: str
    user_id: str
    event_date: date
    event_type: str
    amount: Optional[Decimal]
    currency: str
    category: str
    is_recurring: bool
    linked_event_id: Optional[str]

@dataclass
class ImageReference:
    image_id: str
    user_id: str
    request_id: Optional[str]
    related_event_id: Optional[str]
