"""Ghidra headless integration."""

from pathlib import Path
import json

from .config import HarnessConfig
from .runner import run_command
from .evidence import FunctionEvidence


class GhidraAnalyzer:
    """Imports an XEX and exports normalized per-function evidence."""

    def __init__(self, config: HarnessConfig) -> None:
        if not config.ghidra_headless:
            raise ValueError("tools.ghidra_headless is not configured")
        self.config = config

    def analyze(self) -> Path:
        root = self.config.project_root
        out = root / ".xenonharness" / "analysis"
        project = root / ".xenonharness" / "ghidra"
        out.mkdir(parents=True, exist_ok=True)
        project.mkdir(parents=True, exist_ok=True)
        script_dir = Path(__file__).resolve().parents[2] / "ghidra" / "scripts"
        result = run_command([
            str(self.config.ghidra_headless), str(project), "XenonHarness",
            "-import", str(self.config.xex), "-overwrite",
            "-scriptPath", str(script_dir), "-postScript", "ExportEvidence.py", str(out),
        ], cwd=root, timeout=3600)
        if result.returncode != 0:
            raise RuntimeError(f"Ghidra analysis failed:\n{result.stderr}\n{result.stdout}")
        manifest = out / "functions.json"
        if not manifest.exists():
            raise RuntimeError("Ghidra completed without producing functions.json")
        return manifest

    @staticmethod
    def load_manifest(path: Path) -> list[FunctionEvidence]:
        data = json.loads(path.read_text(encoding="utf-8"))
        result: list[FunctionEvidence] = []
        for item in data:
            evidence_path = path.parent / item["evidence"]
            result.append(FunctionEvidence.from_json(evidence_path))
        return result
