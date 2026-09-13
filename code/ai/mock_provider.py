from typing import Type, TypeVar
from ai.base import LLMProvider
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class MockProvider(LLMProvider):
    """
    A mock provider that allows the pipeline to run locally for development,
    reproducibility, and testing without network access.
    """
    def generate_structured(self, prompt: str, schema: Type[T], model: str = None) -> T:
        # Very crude mock that just returns the default empty schema
        # For a true mock we might use prompt sniffing to return specific test values
        try:
            return schema()
        except:
            # If schema requires arguments, we create a dummy dict
            fields = schema.model_fields
            dummy_data = {}
            for k, v in fields.items():
                if v.annotation == str:
                    dummy_data[k] = "mock"
                elif v.annotation == int or v.annotation == float:
                    dummy_data[k] = 0
                elif v.annotation == bool:
                    dummy_data[k] = False
                elif v.annotation == list:
                    if k == "willing_to_stop":
                        dummy_data[k] = []
                    elif k == "willing_to_reduce":
                        dummy_data[k] = []
                    else:
                        dummy_data[k] = []
                else:
                    dummy_data[k] = None
            return schema(**dummy_data)

    def analyze_image(self, image_path: str, prompt: str, schema: Type[T], model: str = None) -> T:
        return self.generate_structured(prompt, schema, model)
        
    def generate(self, prompt: str, model: str = None) -> str:
        return "Mock response generated successfully."
