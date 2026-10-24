"""Autonomous target -> agent -> build -> verify -> retry orchestration."""

from dataclasses import dataclass
from pathlib import Path

from .agents import Agent
from .config import HarnessConfig
from .evidence import FunctionEvidence
from .prompting import build_prompt, write_prompt
from .scheduler import select_next
from .state import StateDB
from .verification import CommandVerifier, VerificationResult


@dataclass(slots=True)
class RunSummary:
    processed: int = 0
    matched: int = 0
    blocked: int = 0


class Orchestrator:
    """Coordinates deterministic tooling around a replaceable coding agent."""

    def __init__(self, config: HarnessConfig, state: StateDB) -> None:
        self.config = config
        self.state = state
        self.agent = Agent(config.agent_command)
        self.verifier = CommandVerifier(config.project_root, config.build_command,
                                        config.verify_command, config.verification_result)
        self.template = (config.project_root / "prompts" / "decompile.md").read_text(encoding="utf-8")
        self.work_root = config.project_root / ".xenonharness" / "work"
        self.evidence_root = config.project_root / ".xenonharness" / "evidence"

    def _evidence(self, address: int) -> FunctionEvidence:
        path = self.evidence_root / f"{address:08X}.json"
        if not path.exists():
            raise FileNotFoundError(f"Missing evidence for 0x{address:08X}: {path}")
        return FunctionEvidence.from_json(path)

    @staticmethod
    def _feedback(result: VerificationResult) -> str:
        parts = [f"Score: {result.score:.4f}%", result.summary]
        if result.stderr:
            parts.append("Verifier stderr:\n" + result.stderr[-6000:])
        if result.stdout:
            parts.append("Verifier stdout:\n" + result.stdout[-6000:])
        return "\n\n".join(part for part in parts if part)

    def run_function(self, address: int) -> bool:
        evidence = self._evidence(address)
        workspace = self.work_root / f"{address:08X}"
        workspace.mkdir(parents=True, exist_ok=True)
        feedback = ""

        for attempt in range(1, self.config.max_attempts + 1):
            prompt = build_prompt(self.template, evidence, feedback)
            prompt_path = write_prompt(workspace / f"attempt-{attempt:03d}.md", prompt)
            agent_result = self.agent.execute(prompt_path, self.config.project_root)
            if not agent_result.ok:
                feedback = "Agent command failed:\n" + agent_result.stderr[-6000:]
                self.state.record_attempt(address, 0.0, feedback)
                continue

            result = self.verifier.verify(address)
            self.state.record_attempt(address, result.score, result.summary)
            if result.matched:
                return True
            feedback = self._feedback(result)

        self.state.set_status(address, "blocked")
        return False

    def run(self, limit: int | None = None) -> RunSummary:
        summary = RunSummary()
        while limit is None or summary.processed < limit:
            target = select_next(self.state.list_functions())
            if target is None:
                break
            try:
                matched = self.run_function(target.address)
            except (OSError, ValueError, KeyError) as exc:
                self.state.record_attempt(target.address, 0.0, f"orchestrator error: {exc}")
                self.state.set_status(target.address, "blocked")
                matched = False
            summary.processed += 1
            if matched:
                summary.matched += 1
            else:
                summary.blocked += 1
        return summary
