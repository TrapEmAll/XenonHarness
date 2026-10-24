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
    build_command: str = ""
    verify_command: str = ""
    verification_result: Path = Path(".xenonharness/verification.json")
    max_attempts: int = 20

    @classmethod
    def load(cls, path: Path) -> "HarnessConfig":
        path = path.resolve()
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        root = path.parent
        tools = data.get("tools", {})
        agent = data.get("agent", {})
        run = data.get("run", {})
        verification = data.get("verification", {})

        def optional_path(value: str | None) -> Path | None:
            if not value:
                return None
            candidate = Path(value).expanduser()
            return candidate if candidate.is_absolute() else (root / candidate).resolve()

        xex = Path(data["project"]["xex"]).expanduser()
        if not xex.is_absolute():
            xex = (root / xex).resolve()
        result = Path(verification.get("result", ".xenonharness/verification.json"))
        if not result.is_absolute():
            result = (root / result).resolve()
        return cls(project_root=root, xex=xex,
                   ghidra_headless=optional_path(tools.get("ghidra_headless")),
                   xenonrecomp=optional_path(tools.get("xenonrecomp")),
                   objdiff=optional_path(tools.get("objdiff")),
                   agent_command=agent.get("command", "codex"),
                   build_command=verification.get("build_command", ""),
                   verify_command=verification.get("command", ""),
                   verification_result=result,
                   max_attempts=int(run.get("max_attempts", 20)))
