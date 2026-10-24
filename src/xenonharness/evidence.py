"""Normalized reverse-engineering evidence exchanged between tools and agents."""

from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass(slots=True)
class FunctionEvidence:
    """All static evidence the agent may use for one target function."""

    address: int
    name: str
    size: int
    disassembly: str = ""
    decompilation: str = ""
    callers: list[str] = field(default_factory=list)
    callees: list[str] = field(default_factory=list)
    strings: list[str] = field(default_factory=list)
    globals: list[str] = field(default_factory=list)

    @classmethod
    def from_json(cls, path: Path) -> "FunctionEvidence":
        data = json.loads(path.read_text(encoding="utf-8"))
        address = data["address"]
        if isinstance(address, str):
            address = int(address, 0)
        return cls(address=address, name=data["name"], size=int(data.get("size", 0)),
                   disassembly=data.get("disassembly", ""),
                   decompilation=data.get("decompilation", ""),
                   callers=list(data.get("callers", [])), callees=list(data.get("callees", [])),
                   strings=list(data.get("strings", [])), globals=list(data.get("globals", [])))

    def render(self) -> str:
        """Render deterministic evidence text for an agent prompt."""
        def section(name: str, value: object) -> str:
            if isinstance(value, list):
                value = "\n".join(str(item) for item in value) or "(none)"
            return f"## {name}\n{value or '(none)'}"

        return "\n\n".join([
            f"# Function {self.name} @ 0x{self.address:08X}\nSize: {self.size} bytes",
            section("Callers", self.callers), section("Callees", self.callees),
            section("Referenced strings", self.strings), section("Globals", self.globals),
            section("Ghidra decompilation", self.decompilation),
            section("PowerPC disassembly", self.disassembly),
        ])
