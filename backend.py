import os
from typing import List, Dict, Optional

# OpenAI (cloud) — requires OPENAI_API_KEY
try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore

# Optional: Ollama (local) — requires 'ollama' Python package and local server
try:
    import ollama
except Exception:
    ollama = None  # type: ignore


class SGPTBackend:
    def __init__(self, backend: str = "openai", model: str = "gpt-4o-mini"):
        self.backend = backend
        self.model = model

        if backend == "openai":
            if OpenAI is None:
                raise RuntimeError("openai package not installed. Install 'openai>=1.0.0'.")
            api_key = os.getenv("OPENAI_API_KEY", "").strip()
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY not set. Export it or put it in a .env file.")
            self.client = OpenAI()
        elif backend == "ollama":
            if ollama is None:
                raise RuntimeError("ollama package not installed. Install 'ollama' or choose backend=openai.")
        else:
            raise ValueError("backend must be 'openai' or 'ollama'")

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        if self.backend == "openai":
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )
            return (resp.choices[0].message.content or "").strip()

        elif self.backend == "ollama":
            # Simple streaming disabled; just get full response
            out = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return (out.get("message", {}).get("content", "")).strip()

        else:
            raise ValueError("Unsupported backend.")
