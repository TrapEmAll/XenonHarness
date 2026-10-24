"""Prioritize functions that provide the best autonomous progress per attempt."""

from .models import FunctionRecord, FunctionStatus


def priority(function: FunctionRecord) -> float:
    """Score a function; higher values should generally be attempted first."""
    score = 100.0
    score -= min(function.size / 8, 35)
    score -= min(function.complexity * 3, 30)
    score -= function.indirect_branches * 12
    score -= function.unknown_globals * 4
    score -= function.attempts * 3
    score += min(function.callees * 1.5, 8)
    # Near matches are valuable because a small correction can finish them.
    score += function.best_score * 0.25
    return score


def select_next(functions: list[FunctionRecord]) -> FunctionRecord | None:
    """Return the highest-value unfinished function."""
    candidates = [f for f in functions if f.status == FunctionStatus.PENDING]
    return max(candidates, key=priority, default=None)
