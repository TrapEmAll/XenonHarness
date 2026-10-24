"""Prompt construction from normalized evidence and previous verification results."""

from pathlib import Path

from .evidence import FunctionEvidence


def build_prompt(template: str, evidence: FunctionEvidence, previous_feedback: str = "") -> str:
    """Create a bounded, reproducible worker prompt for one function."""
    sections = [
        template.rstrip(),
        "\n## Target evidence",
        f"Address: {evidence.address_hex}",
        f"Name: {evidence.name}",
        f"Size: {evidence.size}",
        "\n### Decompiler output\n" + (evidence.decompiler or "(unavailable)"),
        "\n### PowerPC disassembly\n" + (evidence.disassembly or "(unavailable)"),
        "\n### Callers\n" + "\n".join(evidence.callers or ["(none known)"]),
        "\n### Callees\n" + "\n".join(evidence.callees or ["(none known)"]),
        "\n### Strings\n" + "\n".join(evidence.strings or ["(none known)"]),
        "\n### Globals\n" + "\n".join(evidence.globals or ["(none known)"]),
    ]
    if previous_feedback:
        sections.extend(["\n## Previous verification feedback", previous_feedback.rstrip()])
    return "\n".join(sections) + "\n"


def write_prompt(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
