from pathlib import Path

from cobalt_cli_linux.executor import ShellExecutor
from cobalt_cli_linux.history import ConversationHistory


def test_history_round_trip(tmp_path: Path) -> None:
    history = ConversationHistory(path=tmp_path / "history.json")
    history.add("user", "hello")
    history.add("assistant", "hi")

    assert history.messages[0]["role"] == "user"
    assert history.messages[0]["content"] == "hello"
    assert history.messages[1]["role"] == "assistant"
    assert history.messages[1]["content"] == "hi"


def test_shell_executor_runs_command() -> None:
    result = ShellExecutor().run("printf 'ok'")

    assert result.returncode == 0
    assert result.stdout.strip() == "ok"
    assert result.stderr == ""
