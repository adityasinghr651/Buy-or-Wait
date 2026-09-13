import json
import hashlib
from pathlib import Path
from typing import Dict, Any

CACHE_FILE = Path(__file__).parent.parent.parent / "evaluation" / "ai_cache.json"

class AICache:
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self._load()
        
    def _load(self):
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r') as f:
                try:
                    self.cache = json.load(f)
                except json.JSONDecodeError:
                    self.cache = {}
                    
    def _save(self):
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            json.dump(self.cache, f, indent=2)
            
    def _hash(self, model: str, prompt: str) -> str:
        s = f"{model}::{prompt}"
        return hashlib.sha256(s.encode('utf-8')).hexdigest()
        
    def get(self, model: str, prompt: str) -> Any:
        h = self._hash(model, prompt)
        return self.cache.get(h)
        
    def set(self, model: str, prompt: str, response: Any):
        h = self._hash(model, prompt)
        self.cache[h] = response
        self._save()
