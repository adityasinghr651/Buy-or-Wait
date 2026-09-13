from ai.base import LLMProvider
from ai.config import AI_PROVIDER
from ai.mock_provider import MockProvider

_instance = None

def get_provider() -> LLMProvider:
    global _instance
    if _instance is not None:
        return _instance
        
    if AI_PROVIDER == "mock":
        _instance = MockProvider()
    elif AI_PROVIDER == "google-genai":
        from ai.gemini_provider import GeminiProvider
        _instance = GeminiProvider()
    else:
        # Fallback to mock if unknown provider
        print(f"Warning: Unknown AI_PROVIDER {AI_PROVIDER}. Using mock.")
        _instance = MockProvider()
        
    return _instance
