"""Build and objective verification adapters."""

from dataclasses import dataclass
import json
from pathlib import Path
import shlex

from .runner import run_command


@dataclass(slots=True)
class VerificationResult:
    score: float
    matched: bool
    summary: str
    stdout: str = ""
    stderr: str = ""


class CommandVerifier:
    """Runs configured build/verification commands and parses a machine result file.

    The verifier intentionally does not ask an LLM whether code is correct. The external
    verification command must write JSON containing at least {"score": <0..100>}.
    """

    def __init__(self, root: Path, build_command: str, verify_command: str,
                 result_file: Path) -> None:
        self.root = root
        self.build_command = build_command
        self.verify_command = verify_command
        self.result_file = result_file

    def verify(self, address: int) -> VerificationResult:
        env = {"XENONHARNESS_FUNCTION": f"0x{address:08X}"}
        build = run_command(shlex.split(self.build_command), cwd=self.root, timeout=900, env=env)
        if build.returncode != 0:
            return VerificationResult(0.0, False, "build failed", build.stdout, build.stderr)
        verify = run_command(shlex.split(self.verify_command), cwd=self.root, timeout=300, env=env)
        if verify.returncode != 0:
            return VerificationResult(0.0, False, "verification command failed",
                                      verify.stdout, verify.stderr)
        if not self.result_file.exists():
            return VerificationResult(0.0, False, "verification result file missing",
                                      verify.stdout, verify.stderr)
        data = json.loads(self.result_file.read_text(encoding="utf-8"))
        score = max(0.0, min(100.0, float(data["score"])))
        summary = str(data.get("summary", ""))
        return VerificationResult(score, score >= 100.0, summary, verify.stdout, verify.stderr)
