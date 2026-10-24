"""TOML project configuration."""

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True, slots=True)
class HarnessConfig:
    project_root: Path
    xex: Path
    ghidra_headless: Path | None
    xenonrecomp: Path | None
    objdiff: Path | None
    agent_command: str
    max_attempts: int = 20

    @classmethod
    def load(cls, path: Path) -> "HarnessConfig":
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        root = path.parent.resolve()
        tools = data.get("tools", {})
        agent = data.get("agent", {})
        run = data.get("run", {})

        def optional_path(value: str | None) -> Path | None:
            return Path(value).expanduser() if value else None

        return cls(
            project_root=root,
            xex=(root / data["project"]["xex"]).resolve(),
            ghidra_headless=optional_path(tools.get("ghidra_headless")),
            xenonrecomp=optional_path(tools.get("xenonrecomp")),
            objdiff=optional_path(tools.get("objdiff")),
            agent_command=agent.get("command", "codex"),
            max_attempts=int(run.get("max_attempts", 20)),
        )
