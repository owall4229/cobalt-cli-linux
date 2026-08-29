from __future__ import annotations

import json
from typing import Any

import httpx


class DeepSeekAPIError(RuntimeError):
    """Raised when the DeepSeek API rejects a request."""


class DeepSeekClient:
    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: str = "https://api.deepseek.com") -> None:
        if not api_key:
            raise ValueError("DeepSeek API key is required")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def chat_completion(self, messages: list[dict[str, str]], temperature: float = 0.2, max_tokens: int = 1024) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(f"{self.base_url}/v1/chat/completions", headers=headers, json=payload)

        if response.status_code != 200:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text
            raise DeepSeekAPIError(f"DeepSeek API request failed ({response.status_code}): {detail}")

        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise DeepSeekAPIError("DeepSeek API returned no choices")
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if not isinstance(content, str):
            return json.dumps(content)
        return content.strip()
