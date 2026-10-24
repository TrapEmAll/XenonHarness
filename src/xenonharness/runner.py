"""Process execution helpers shared by external-tool adapters."""

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess


@dataclass(slots=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run_command(command: list[str], cwd: Path | None = None, timeout: int = 600,
                env: dict[str, str] | None = None, stdin: str | None = None) -> CommandResult:
    """Run an external tool without a shell, optionally overlaying environment variables."""
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    process = subprocess.run(command, cwd=cwd, text=True, input=stdin, capture_output=True,
                             timeout=timeout, check=False, env=process_env)
    return CommandResult(command, process.returncode, process.stdout, process.stderr)


# Backward-compatible alias for the initial public API.
run = run_command
