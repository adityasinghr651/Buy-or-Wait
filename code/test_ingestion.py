import sys
from pathlib import Path

# Add code directory to python path
CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

from config import (
    SAMPLE_REQUESTS_FILE, PROFILES_FILE, OPTIONS_FILE,
    MESSAGES_FILE, EXCHANGE_RATES_FILE
)
from ingestion.data_loader import DataLoader
from utils.currency import CurrencyConverter

def test_ingestion():
    print("Loading data...")
    loader = DataLoader()
    
    try:
        loader.load_all(
            requests_file=SAMPLE_REQUESTS_FILE,
            profiles_file=PROFILES_FILE,
            options_file=OPTIONS_FILE,
            messages_file=MESSAGES_FILE,
            rates_file=EXCHANGE_RATES_FILE
        )
        print("Data loaded successfully!")
        print(f"Requests loaded: {len(loader.requests)}")
        print(f"Profiles loaded: {len(loader.profiles)}")
        print(f"Payment Options loaded: {sum(len(opts) for opts in loader.payment_options.values())}")
        print(f"Messages loaded: {len(loader.messages)}")
        print(f"Exchange Rates loaded: {len(loader.exchange_rates)}")
        
        # Test currency converter
        converter = CurrencyConverter(loader.exchange_rates)
        print("\nTesting currency converter (USD to IDR on 2023-10-15):")
        rate = converter.get_rate("USD", "IDR", loader.exchange_rates[0].rate_date)
        print(f"Rate: {rate}")
        
    except Exception as e:
        print(f"Error during loading: {e}")

if __name__ == "__main__":
    test_ingestion()
