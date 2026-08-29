from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConversationHistory:
    """Persist a conversation between a user and assistant in JSON format."""

    def __init__(self, path: str | Path = "~/.cobalt/history.json") -> None:
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._messages: list[dict[str, str]] = []
        self.load()

    @property
    def messages(self) -> list[dict[str, str]]:
        return self._messages

    def load(self) -> list[dict[str, str]]:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = []
            if isinstance(data, list):
                self._messages = [
                    {"role": str(item.get("role", "user")), "content": str(item.get("content", ""))}
                    for item in data
                    if isinstance(item, dict)
                ]
            else:
                self._messages = []
        else:
            self._messages = []
        return self._messages

    def add(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._messages, indent=2), encoding="utf-8")

    def clear(self) -> None:
        self._messages = []
        self.save()

    def latest(self, count: int = 10) -> list[dict[str, str]]:
        return self._messages[-count:]

    def __iter__(self):
        return iter(self._messages)

    def __len__(self) -> int:
        return len(self._messages)

    def __getitem__(self, index: int) -> dict[str, str]:
        return self._messages[index]
