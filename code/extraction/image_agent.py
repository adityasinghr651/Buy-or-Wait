import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

IMAGE_EXTRACTION_PROMPT = """
You are a strict financial OCR agent.
Look at this image of an invoice, receipt, or screenshot.
Extract the final total amount required to be paid.

Output MUST be a single valid JSON object:
{
  "amount": <float or null if not found>,
  "currency": "<3 letter code or null>"
}
"""

class ImageExtractionAgent:
    def __init__(self, vision_llm_client=None):
        self.vision_llm_client = vision_llm_client

    def _call_vision_llm(self, image_path: str, prompt: str) -> str:
        if self.vision_llm_client:
            # e.g., self.vision_llm_client.generate_content([image, prompt])
            raise NotImplementedError("Vision LLM client not implemented.")
            
        # Mock behavior
        return '{"amount": 1000.0, "currency": "ZAR"}'

    def process_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        try:
            raw_response = self._call_vision_llm(image_path, IMAGE_EXTRACTION_PROMPT)
            clean_response = raw_response.strip().removeprefix("```json").removesuffix("```").strip()
            fact = json.loads(clean_response)
            return fact
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from Vision LLM for image {image_path}")
            return None
        except Exception as e:
            logger.error(f"Error extracting image {image_path}: {e}")
            return None
