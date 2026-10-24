"""Coding-agent adapter.

The harness intentionally treats the model as a replaceable worker. Verification,
state and scheduling remain deterministic components owned by XenonHarness.
"""

from dataclasses import dataclass
from pathlib import Path
import shlex

from .runner import CommandResult, run


@dataclass(slots=True)
class Agent:
    command: str

    def execute(self, prompt_file: Path, workspace: Path) -> CommandResult:
        """Invoke an agent command with a prompt file path appended.

        Users can point this at a wrapper for Codex, Claude Code, or another agent.
        A wrapper keeps provider-specific flags out of the harness core.
        """
        argv = shlex.split(self.command, posix=False)
        argv.append(str(prompt_file))
        return run(argv, cwd=workspace, timeout=3600)
