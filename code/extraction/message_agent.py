from pathlib import Path
from extraction.evidence import AgentOutput
from ai.provider import get_provider

class MessageExtractionAgent:
    def __init__(self):
        self.provider = get_provider()
        prompt_path = Path(__file__).parent.parent / "ai" / "prompts" / "message_extraction_v1.txt"
        with open(prompt_path, 'r') as f:
            self.base_prompt = f.read()

    def extract_facts(self, message_text: str) -> AgentOutput:
        prompt = self.base_prompt.format(message_text=message_text)
        try:
            return self.provider.generate_structured(prompt, AgentOutput)
        except Exception as e:
            # Fallback to empty if AI fails
            print(f"Message Extraction Failed: {e}")
            return AgentOutput()
