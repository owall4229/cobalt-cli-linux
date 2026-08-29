from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CommandResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    duration: float

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class ShellExecutor:
    """Execute commands in a POSIX shell environment."""

    def __init__(self, shell: str = "/bin/bash") -> None:
        self.shell = shell

    def run(
        self,
        command: str,
        cwd: Optional[str | Path] = None,
        timeout: Optional[float] = None,
        env: Optional[dict[str, str]] = None,
    ) -> CommandResult:
        started = time.monotonic()
        completed = subprocess.run(
            command,
            shell=True,
            executable=self.shell,
            cwd=str(cwd) if cwd is not None else None,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        duration = time.monotonic() - started
        return CommandResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            duration=duration,
        )
