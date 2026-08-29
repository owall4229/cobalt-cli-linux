from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_MODEL = "deepseek-chat"
DEFAULT_BASE_URL = "https://api.deepseek.com"


@dataclass
class Settings:
    api_key: str | None = None
    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    history_path: str | Path = "~/.cobalt/history.json"
    shell: str = "/bin/bash"
    temperature: float = 0.2
    max_tokens: int = 1024

    def __post_init__(self) -> None:
        if self.api_key is None:
            self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.model:
            self.model = os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL)
        if not self.base_url:
            self.base_url = os.getenv("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL)
        if self.history_path is None:
            self.history_path = os.getenv("COBALT_HISTORY_PATH", str(Path.home() / ".cobalt" / "history.json"))
        self.history_path = Path(self.history_path).expanduser()
        if not self.shell:
            self.shell = os.getenv("SHELL", "/bin/bash")

    @property
    def api_key_configured(self) -> bool:
        return bool(self.api_key)
