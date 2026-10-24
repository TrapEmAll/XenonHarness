"""Persistent SQLite state for long-running autonomous sessions."""

import sqlite3
from pathlib import Path

from .models import FunctionRecord, FunctionStatus

SCHEMA = """
CREATE TABLE IF NOT EXISTS functions (
 address INTEGER PRIMARY KEY, name TEXT NOT NULL, size INTEGER NOT NULL DEFAULT 0,
 callers INTEGER NOT NULL DEFAULT 0, callees INTEGER NOT NULL DEFAULT 0,
 unknown_globals INTEGER NOT NULL DEFAULT 0, indirect_branches INTEGER NOT NULL DEFAULT 0,
 complexity INTEGER NOT NULL DEFAULT 1, best_score REAL NOT NULL DEFAULT 0,
 attempts INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'pending'
);
CREATE TABLE IF NOT EXISTS attempts (
 id INTEGER PRIMARY KEY AUTOINCREMENT, address INTEGER NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, score REAL NOT NULL,
 summary TEXT NOT NULL DEFAULT '', FOREIGN KEY(address) REFERENCES functions(address)
);
"""


class StateDB:
    """Persistence API deliberately independent from the AI provider."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(SCHEMA)

    def upsert_function(self, function: FunctionRecord) -> None:
        self.connection.execute(
            """INSERT INTO functions
            (address,name,size,callers,callees,unknown_globals,indirect_branches,complexity,
             best_score,attempts,status) VALUES (?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(address) DO UPDATE SET name=excluded.name,size=excluded.size,
             callers=excluded.callers,callees=excluded.callees,
             unknown_globals=excluded.unknown_globals,
             indirect_branches=excluded.indirect_branches,complexity=excluded.complexity""",
            (function.address, function.name, function.size, function.callers, function.callees,
             function.unknown_globals, function.indirect_branches, function.complexity,
             function.best_score, function.attempts, function.status.value),
        )
        self.connection.commit()

    def list_functions(self) -> list[FunctionRecord]:
        rows = self.connection.execute("SELECT * FROM functions ORDER BY address").fetchall()
        return [FunctionRecord(**{**dict(row), "status": FunctionStatus(row["status"])}) for row in rows]

    def set_status(self, address: int, status: FunctionStatus | str) -> None:
        value = FunctionStatus(status).value
        cursor = self.connection.execute("UPDATE functions SET status=? WHERE address=?", (value, address))
        if cursor.rowcount != 1:
            raise KeyError(f"Unknown function address 0x{address:08X}")
        self.connection.commit()

    def record_attempt(self, address: int, score: float, summary: str = "") -> None:
        score = max(0.0, min(100.0, float(score)))
        with self.connection:
            self.connection.execute(
                "INSERT INTO attempts(address,score,summary) VALUES (?,?,?)",
                (address, score, summary),
            )
            cursor = self.connection.execute(
                """UPDATE functions SET attempts=attempts+1, best_score=MAX(best_score, ?),
                status=CASE WHEN ? >= 100.0 THEN 'matched' ELSE status END WHERE address=?""",
                (score, score, address),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Unknown function address 0x{address:08X}")
