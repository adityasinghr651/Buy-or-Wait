from pathlib import Path
from extraction.evidence import AgentOutput
from ai.provider import get_provider

class ImageExtractionAgent:
    def __init__(self):
        self.provider = get_provider()
        prompt_path = Path(__file__).parent.parent / "ai" / "prompts" / "image_extraction_v1.txt"
        with open(prompt_path, 'r') as f:
            self.base_prompt = f.read()

    def extract_facts(self, image_path: str, context: str = "") -> AgentOutput:
        prompt = self.base_prompt.format(image_context=context)
        try:
            return self.provider.analyze_image(image_path, prompt, AgentOutput)
        except Exception as e:
            # Fallback to empty if AI fails
            print(f"Image Extraction Failed: {e}")
            return AgentOutput()
