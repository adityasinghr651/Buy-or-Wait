import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class LLMProvider(ABC):
    """
    Abstract base class for all AI providers to ensure the financial pipeline
    never depends directly on OpenAI, Gemini, or any specific API.
    """
    
    @abstractmethod
    def generate_structured(self, prompt: str, schema: Type[T], model: Optional[str] = None) -> T:
        """
        Generate structured output conforming to a Pydantic schema.
        """
        pass

    @abstractmethod
    def analyze_image(self, image_path: str, prompt: str, schema: Type[T], model: Optional[str] = None) -> T:
        """
        Analyze an image and extract structured facts.
        """
        pass
        
    @abstractmethod
    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate unstructured text (e.g. for explanation generation).
        """
        pass
