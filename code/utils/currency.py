from decimal import Decimal
from typing import List, Optional
from datetime import date
from models.state import ExchangeRate

class CurrencyConverter:
    def __init__(self, exchange_rates: List[ExchangeRate]):
        self.exchange_rates = exchange_rates
        self.rate_map = {}
        for rate in exchange_rates:
            key = (rate.from_currency, rate.to_currency, rate.rate_date)
            self.rate_map[key] = rate.rate

    def get_rate(self, from_currency: str, to_currency: str, target_date: date) -> Decimal:
        if from_currency == to_currency:
            return Decimal("1.0")
            
        # Try to find exact match
        key = (from_currency, to_currency, target_date)
        if key in self.rate_map:
            return self.rate_map[key]
            
        # Fallback to the closest earlier date if exact date is missing
        # In a strict hackathon, exchange_rates might only update monthly
        applicable_rates = [
            r for r in self.exchange_rates 
            if r.from_currency == from_currency and r.to_currency == to_currency and r.rate_date <= target_date
        ]
        if applicable_rates:
            # Sort by date descending and pick the most recent one
            applicable_rates.sort(key=lambda r: r.rate_date, reverse=True)
            return applicable_rates[0].rate

        # If we can't find a direct rate, we would ideally fail safe or return 1.0.
        raise ValueError(f"No exchange rate found for {from_currency} to {to_currency} on or before {target_date}")

    def convert(self, amount: Decimal, from_currency: str, to_currency: str, target_date: date) -> Decimal:
        if not amount:
            return Decimal("0.0")
        if from_currency == to_currency:
            return amount
        rate = self.get_rate(from_currency, to_currency, target_date)
        return amount * rate
