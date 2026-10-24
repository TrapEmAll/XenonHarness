"""Process execution helpers shared by external-tool adapters."""

from dataclasses import dataclass
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


def run(command: list[str], cwd: Path | None = None, timeout: int = 600) -> CommandResult:
    """Run an external tool without invoking a shell."""
    process = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return CommandResult(command, process.returncode, process.stdout, process.stderr)
