"""Adapters for the upstream XenonRecomp toolchain."""

from dataclasses import dataclass
from pathlib import Path

from .runner import CommandResult, run


@dataclass(slots=True)
class XenonToolchain:
    """Run XenonAnalyse/XenonRecomp without coupling the harness to their source tree."""

    recomp: Path
    analyse: Path | None = None

    def analyse_xex(self, xex: Path, output_toml: Path) -> CommandResult:
        if self.analyse is None:
            raise RuntimeError("XenonAnalyse path is not configured")
        output_toml.parent.mkdir(parents=True, exist_ok=True)
        return run([str(self.analyse), str(xex), str(output_toml)], cwd=output_toml.parent)

    def recompile(self, config_toml: Path, ppc_context: Path) -> CommandResult:
        """Translate the configured XEX to C++ using upstream XenonRecomp."""
        return run([str(self.recomp), str(config_toml), str(ppc_context)], cwd=config_toml.parent)
