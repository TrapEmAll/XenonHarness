from pathlib import Path

from xenonharness.models import FunctionRecord, FunctionStatus
from xenonharness.state import StateDB


def test_attempt_matching_and_status(tmp_path: Path):
    db = StateDB(tmp_path / "state.db")
    db.upsert_function(FunctionRecord(address=0x82000000, name="test"))
    db.record_attempt(0x82000000, 75.5, "close")
    fn = db.list_functions()[0]
    assert fn.best_score == 75.5
    assert fn.attempts == 1
    assert fn.status == FunctionStatus.PENDING
    db.record_attempt(0x82000000, 100, "matched")
    assert db.list_functions()[0].status == FunctionStatus.MATCHED


def test_explicit_status(tmp_path: Path):
    db = StateDB(tmp_path / "state.db")
    db.upsert_function(FunctionRecord(address=1, name="blocked"))
    db.set_status(1, FunctionStatus.BLOCKED)
    assert db.list_functions()[0].status == FunctionStatus.BLOCKED
