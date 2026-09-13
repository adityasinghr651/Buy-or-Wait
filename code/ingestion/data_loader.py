import csv
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from models.state import (
    UserRequest, FinancialProfile, PaymentOption, 
    Message, ExchangeRate
)

def parse_date(date_str: str):
    if not date_str:
        return None
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def parse_decimal(decimal_str: str) -> Optional[Decimal]:
    if not decimal_str:
        return None
    return Decimal(decimal_str)

def parse_bool(bool_str: str) -> bool:
    return bool_str.lower() in ("true", "1", "yes")

def parse_list(list_str: str) -> List[str]:
    if not list_str or list_str.lower() == "none":
        return []
    return [item.strip() for item in list_str.split("|") if item.strip()]

class DataLoader:
    def __init__(self):
        self.requests: Dict[str, UserRequest] = {}
        self.profiles: Dict[str, FinancialProfile] = {}
        self.payment_options: Dict[str, List[PaymentOption]] = {}
        self.messages: List[Message] = []
        self.exchange_rates: List[ExchangeRate] = []
        self.events: List[Dict] = []

    def _read_csv(self, filepath) -> List[Dict]:
        if not filepath.exists():
            return []
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def load_requests(self, filepath):
        rows = self._read_csv(filepath)
        for row in rows:
            req = UserRequest(
                request_id=row["request_id"],
                user_id=row["user_id"],
                request_date=parse_date(row["request_date"]),
                request_type=row["request_type"],
                requested_amount=parse_decimal(row["requested_amount"]),
                desired_completion_date=parse_date(row["desired_completion_date"]),
                allows_partial_payment=parse_bool(row["allows_partial_payment"]),
                request_text=row.get("request_text", "")
            )
            self.requests[req.request_id] = req

    def load_profiles(self, filepath):
        rows = self._read_csv(filepath)
        for row in rows:
            max_inst = row.get("max_installment_months", "").strip()
            max_inst_val = int(max_inst) if max_inst else None
            
            prof = FinancialProfile(
                user_id=row["user_id"],
                home_currency=row["home_currency"],
                current_available_balance=parse_decimal(row["current_available_balance"]),
                minimum_balance_to_keep=parse_decimal(row["minimum_balance_to_keep"]),
                financial_priorities=parse_list(row.get("financial_priorities", "")),
                expense_categories_to_protect=parse_list(row.get("expense_categories_to_protect", "")),
                expense_categories_user_is_willing_to_reduce=parse_list(row.get("expense_categories_user_is_willing_to_reduce", "")),
                expense_categories_user_is_willing_to_stop=parse_list(row.get("expense_categories_user_is_willing_to_stop", "")),
                payment_methods_user_will_consider=parse_list(row.get("payment_methods_user_will_consider", "")),
                max_installment_months=max_inst_val
            )
            self.profiles[prof.user_id] = prof

    def load_payment_options(self, filepath):
        rows = self._read_csv(filepath)
        for row in rows:
            freq_str = row.get("payment_frequency_days", "")
            freq = int(freq_str) if freq_str else 0
            
            opt = PaymentOption(
                payment_option_id=row["payment_option_id"],
                request_id=row["request_id"],
                payment_method=row["payment_method"],
                payment_amount=parse_decimal(row["payment_amount"]),
                number_of_payments=int(row["number_of_payments"]),
                first_payment_date=parse_date(row["first_payment_date"]),
                payment_frequency_days=freq,
                financing_fee=parse_decimal(row.get("financing_fee", "0")),
                total_payable_amount=parse_decimal(row["total_payable_amount"])
            )
            if opt.request_id not in self.payment_options:
                self.payment_options[opt.request_id] = []
            self.payment_options[opt.request_id].append(opt)

    def load_messages(self, filepath):
        rows = self._read_csv(filepath)
        for row in rows:
            msg = Message(
                message_id=row["message_id"],
                user_id=row["user_id"],
                request_id=row.get("request_id") if row.get("request_id") else None,
                related_event_id=row.get("related_event_id") if row.get("related_event_id") else None,
                sent_at=row["sent_at"],
                source_type=row["source_type"],
                message_text=row["message_text"]
            )
            self.messages.append(msg)

    def load_exchange_rates(self, filepath):
        rows = self._read_csv(filepath)
        for row in rows:
            rate = ExchangeRate(
                rate_date=parse_date(row["rate_date"]),
                from_currency=row["from_currency"],
                to_currency=row["to_currency"],
                rate=parse_decimal(row["rate"])
            )
            self.exchange_rates.append(rate)
            
    def load_events(self, filepath):
        self.events = self._read_csv(filepath)

    def load_all(self, requests_file, profiles_file, options_file, messages_file, rates_file, events_file=None):
        self.load_requests(requests_file)
        self.load_profiles(profiles_file)
        self.load_payment_options(options_file)
        self.load_messages(messages_file)
        self.load_exchange_rates(rates_file)
        if events_file:
            self.load_events(events_file)
