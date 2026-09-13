import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CODE_DIR))

from extraction.message_agent import MessageExtractionAgent
from extraction.image_agent import ImageExtractionAgent
from models.state import Message

def test_message_agent():
    agent = MessageExtractionAgent()
    
    # Test confirmed income message
    msg1 = Message(
        message_id="m1", user_id="u1", request_id=None, related_event_id=None,
        sent_at="2025-07-29T09:30:00Z", source_type="employer",
        message_text="gaji bulanan Anda naik menjadi IDR 42750000"
    )
    
    facts = agent.process_message(msg1)
    assert len(facts) == 1
    assert facts[0]["fact_type"] == "income_update"
    assert facts[0]["amount"] == 42750000
    assert facts[0]["is_confirmed"] is True
    
    # Test unconfirmed bonus
    msg2 = Message(
        message_id="m2", user_id="u2", request_id=None, related_event_id=None,
        sent_at="2024-06-01T09:30:00Z", source_type="employer",
        message_text="Bonus kuartalan Anda masih menunggu hasil akhir"
    )
    facts2 = agent.process_message(msg2)
    assert len(facts2) == 1
    assert facts2[0]["is_confirmed"] is False

def test_image_agent():
    agent = ImageExtractionAgent()
    fact = agent.process_image("dummy_path.png")
    assert fact is not None
    assert fact["amount"] == 1000.0
    assert fact["currency"] == "ZAR"

if __name__ == "__main__":
    print("Testing extraction agents...")
    test_message_agent()
    test_image_agent()
    print("Extraction agents tests passed!")
