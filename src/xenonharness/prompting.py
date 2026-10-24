"""Prompt construction from normalized evidence and previous verification results."""

from pathlib import Path

from .evidence import FunctionEvidence


def build_prompt(template: str, evidence: FunctionEvidence, previous_feedback: str = "") -> str:
    """Create a bounded, reproducible worker prompt for one function."""
    sections = [template.rstrip(), "\n## Target evidence", evidence.render()]
    if previous_feedback:
        sections.extend(["\n## Previous verification feedback", previous_feedback.rstrip()])
    return "\n".join(sections) + "\n"


def write_prompt(path: Path, text: str) -> Path:
    """Persist the exact prompt used so autonomous attempts are auditable."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
