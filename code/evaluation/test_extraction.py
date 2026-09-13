import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CODE_DIR))

from extraction.message_agent import MessageExtractionAgent
from extraction.image_agent import ImageExtractionAgent
from models.state import Message

def test_message_agent():
    agent = MessageExtractionAgent()
    
    # We patch the provider to return a specific AgentOutput for testing
    # so we don't rely on the empty dummy data from mock_provider
    from extraction.evidence import AgentOutput, ExtractedFact
    
    original_generate = agent.provider.generate_structured
    
    def fake_generate(prompt, schema, model=None):
        if "gaji bulanan" in prompt:
            return AgentOutput(
                facts=[ExtractedFact(
                    fact_type="income",
                    amount=42750000.0,
                    currency="IDR",
                    category="salary",
                    certainty="confirmed",
                    confidence=0.9,
                    source="message",
                    evidence_text="gaji bulanan Anda naik"
                )]
            )
        elif "Bonus kuartalan" in prompt:
            return AgentOutput(
                facts=[ExtractedFact(
                    fact_type="income",
                    amount=0.0,
                    currency="IDR",
                    category="bonus",
                    certainty="uncertain",
                    confidence=0.8,
                    source="message",
                    evidence_text="Bonus kuartalan"
                )]
            )
        return schema()
        
    agent.provider.generate_structured = fake_generate
    
    # Test confirmed income message
    msg1 = Message(
        message_id="m1", user_id="u1", request_id=None, related_event_id=None,
        sent_at="2025-07-29T09:30:00Z", source_type="employer",
        message_text="gaji bulanan Anda naik menjadi IDR 42750000"
    )
    
    output1 = agent.extract_facts(msg1.message_text)
    assert len(output1.facts) == 1
    assert output1.facts[0].fact_type == "income"
    assert output1.facts[0].amount == 42750000.0
    assert output1.facts[0].certainty == "confirmed"
    
    # Test unconfirmed bonus
    msg2 = Message(
        message_id="m2", user_id="u2", request_id=None, related_event_id=None,
        sent_at="2024-06-01T09:30:00Z", source_type="employer",
        message_text="Bonus kuartalan Anda masih menunggu hasil akhir"
    )
    output2 = agent.extract_facts(msg2.message_text)
    assert len(output2.facts) == 1
    assert output2.facts[0].certainty == "uncertain"
    
    # Restore
    agent.provider.generate_structured = original_generate

def test_image_agent():
    agent = ImageExtractionAgent()
    
    from extraction.evidence import AgentOutput, ExtractedFact
    
    original_analyze = agent.provider.analyze_image
    def fake_analyze(image_path, prompt, schema, model=None):
        return AgentOutput(
            facts=[ExtractedFact(
                fact_type="expense",
                amount=1000.0,
                currency="ZAR",
                category="invoice",
                certainty="confirmed",
                confidence=0.9,
                source="image",
                evidence_text="invoice 1000 ZAR"
            )]
        )
    agent.provider.analyze_image = fake_analyze
    
    output = agent.extract_facts("dummy_path.png")
    assert output is not None
    assert len(output.facts) == 1
    assert output.facts[0].amount == 1000.0
    assert output.facts[0].currency == "ZAR"
    
    agent.provider.analyze_image = original_analyze

if __name__ == "__main__":
    print("Testing extraction agents...")
    test_message_agent()
    test_image_agent()
    print("Extraction agents tests passed!")
