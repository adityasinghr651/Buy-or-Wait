import os
from pathlib import Path

# Provide defaults for mock environment
AI_PROVIDER = os.getenv("AI_PROVIDER", "mock")  # Default to mock
AI_MODEL = os.getenv("AI_MODEL", "mock-model")
AI_API_KEY = os.getenv("AI_API_KEY", "")

# Ensure .env.example exists to document required configuration
ENV_EXAMPLE = """
AI_PROVIDER=google-genai
AI_MODEL=gemini-2.5-pro
AI_API_KEY=your_key_here
"""

def ensure_env_example():
    env_path = Path(__file__).parent.parent.parent / ".env.example"
    if not env_path.exists():
        with open(env_path, "w") as f:
            f.write(ENV_EXAMPLE.strip())

ensure_env_example()
