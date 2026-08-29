from __future__ import annotations

import json
import re
from pathlib import Path

from .config import Settings
from .deepseek_client import DeepSeekClient
from .executor import ShellExecutor
from .history import ConversationHistory

SYSTEM_PROMPT = """You are Cobalt, an expert Debian Linux assistant and DevOps engineer.

Your job is to help the user safely operate the system, inspect files, run commands, and maintain a persistent local conversation.

When you need to execute a shell command, read a file, or write to a file, use one of these exact formats in your response:
- COMMAND: <shell command>
- READ_FILE: <path>
- WRITE_FILE: <path>
<content>

If no tool use is required, answer normally.
"""


class CobaltAgent:
    def __init__(self, settings: Settings | None = None, history: ConversationHistory | None = None) -> None:
        self.settings = settings or Settings()
        self.history = history or ConversationHistory(self.settings.history_path)
        self.executor = ShellExecutor(self.settings.shell)
        self.client = DeepSeekClient(
            api_key=self.settings.api_key,
            model=self.settings.model,
            base_url=self.settings.base_url,
        )

    def _build_messages(self, prompt: str) -> list[dict[str, str]]:
        user_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history.latest(20)
        user_messages.append({"role": "user", "content": prompt})
        return user_messages

    def _execute_tool(self, tool_name: str, payload: str) -> str:
        tool_name = tool_name.strip().upper()
        if tool_name == "COMMAND":
            result = self.executor.run(payload)
            output = result.stdout.strip() or ""
            error = result.stderr.strip()
            summary = [f"Exit code: {result.returncode}", f"Stdout: {output}", f"Stderr: {error}"]
            return "\n".join(part for part in summary if part)
        if tool_name == "READ_FILE":
            path = Path(payload.strip())
            return path.read_text(encoding="utf-8")
        if tool_name == "WRITE_FILE":
            if "\n" not in payload:
                raise ValueError("WRITE_FILE requires a path and content on separate lines")
            path_text, content = payload.split("\n", 1)
            path = Path(path_text.strip())
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return f"Wrote {path}"
        raise ValueError(f"Unsupported tool: {tool_name}")

    def _extract_tools(self, response: str) -> list[tuple[str, str]]:
        tools: list[tuple[str, str]] = []
        for line in response.splitlines():
            match = re.match(r"^(COMMAND|READ_FILE|WRITE_FILE):\s*(.*)$", line.strip())
            if match:
                tools.append((match.group(1), match.group(2)))
                continue
        if "WRITE_FILE:" in response:
            match = re.search(r"WRITE_FILE:\s*(.+?)\n(.+)", response, re.DOTALL)
            if match:
                path = match.group(1).strip()
                content = match.group(2)
                tools.append(("WRITE_FILE", f"{path}\n{content}"))
        return tools

    def process(self, prompt: str) -> str:
        if not self.settings.api_key_configured:
            raise RuntimeError("Missing DeepSeek API key. Set the DEEPSEEK_API_KEY environment variable or pass --api-key.")

        self.history.add("user", prompt)
        messages = self._build_messages(prompt)
        response = self.client.chat_completion(messages, temperature=self.settings.temperature, max_tokens=self.settings.max_tokens)

        tool_calls = self._extract_tools(response)
        if not tool_calls:
            self.history.add("assistant", response)
            return response

        tool_results: list[str] = []
        for tool_name, payload in tool_calls:
            try:
                result = self._execute_tool(tool_name, payload)
                tool_results.append(f"{tool_name} result:\n{result}")
            except Exception as exc:  # pragma: no cover - defensive path
                tool_results.append(f"{tool_name} error:\n{exc}")

        final_prompt = "Here are the tool result(s) from my previous action:\n\n" + "\n\n".join(tool_results) + "\n\nPlease provide the final user-facing response based on these results."
        follow_up = self.client.chat_completion(
            [{"role": "system", "content": SYSTEM_PROMPT}] + self.history.latest(20) + [{"role": "user", "content": final_prompt}],
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
        )
        self.history.add("assistant", follow_up)
        return follow_up
