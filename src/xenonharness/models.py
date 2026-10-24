"""Core data models used by the scheduler and persistence layer."""

from dataclasses import dataclass
from enum import StrEnum


class FunctionStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    MATCHED = "matched"
    BLOCKED = "blocked"


@dataclass(slots=True)
class FunctionRecord:
    address: int
    name: str
    size: int = 0
    callers: int = 0
    callees: int = 0
    unknown_globals: int = 0
    indirect_branches: int = 0
    complexity: int = 1
    best_score: float = 0.0
    attempts: int = 0
    status: FunctionStatus = FunctionStatus.PENDING

    @property
    def address_hex(self) -> str:
        """Return the function address in conventional Xbox 360 notation."""
        return f"0x{self.address:08X}"
