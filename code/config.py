import os
from pathlib import Path

# Paths
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Attempt to find dataset in `dataset/` or fallback to root
if (BASE_DIR / "dataset").exists():
    DATA_DIR = BASE_DIR / "dataset"
else:
    DATA_DIR = BASE_DIR

# File paths
REQUESTS_FILE = DATA_DIR / "requests.csv"
SAMPLE_REQUESTS_FILE = DATA_DIR / "sample_requests.csv"
PROFILES_FILE = DATA_DIR / "financial_profiles.csv"
EVENTS_FILE = DATA_DIR / "financial_events.csv"
OPTIONS_FILE = DATA_DIR / "request_payment_options.csv"
MESSAGES_FILE = DATA_DIR / "messages.csv"
IMAGES_FILE = DATA_DIR / "images.csv"
EXCHANGE_RATES_FILE = DATA_DIR / "exchange_rates.csv"
OUTPUT_FILE = BASE_DIR / "output.csv"
