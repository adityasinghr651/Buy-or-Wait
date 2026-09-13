import os
from typing import Type, TypeVar
from pydantic import BaseModel
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types
from ai.base import LLMProvider
from ai.config import AI_API_KEY, AI_MODEL

T = TypeVar('T', bound=BaseModel)

class GeminiProvider(LLMProvider):
    def __init__(self):
        # We assume google-genai is installed.
        api_key = AI_API_KEY or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("AI_API_KEY (or GEMINI_API_KEY) must be set for GeminiProvider")
            
        self.client = genai.Client(api_key=api_key)
        self.default_model = AI_MODEL if AI_MODEL and AI_MODEL != "mock-model" else "gemini-2.5-pro"

    def generate_structured(self, prompt: str, schema: Type[T], model: str = None) -> T:
        model_name = model or self.default_model
        
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.0,
            ),
        )
        
        return schema.model_validate_json(response.text)

    def analyze_image(self, image_path: str, prompt: str, schema: Type[T], model: str = None) -> T:
        model_name = model or self.default_model
        
        # In genai SDK, we upload the file first if needed, or pass it directly.
        # Assuming direct pass for local files for simplicity.
        import PIL.Image
        try:
            image = PIL.Image.open(image_path)
            response = self.client.models.generate_content(
                model=model_name,
                contents=[image, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.0,
                ),
            )
            return schema.model_validate_json(response.text)
        except Exception as e:
            raise RuntimeError(f"Failed to analyze image: {e}")
            
    def generate(self, prompt: str, model: str = None) -> str:
        model_name = model or self.default_model
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
            )
        )
        return response.text
