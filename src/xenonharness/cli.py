"""Command-line interface for XenonHarness."""

from pathlib import Path
import shutil

import typer
from rich.console import Console
from rich.table import Table

from .config import HarnessConfig
from .scheduler import priority, select_next
from .state import StateDB

app = typer.Typer(no_args_is_help=True, help="Autonomous Xbox 360 RE orchestration harness.")
console = Console()


def db_for(config_path: Path) -> StateDB:
    config = HarnessConfig.load(config_path)
    return StateDB(config.project_root / ".xenonharness" / "state.db")


@app.command()
def doctor(config: Path = Path("harness.toml")) -> None:
    """Check local dependencies without modifying the machine."""
    cfg = HarnessConfig.load(config)
    checks = {
        "XEX": cfg.xex.exists(),
        "Ghidra": bool(cfg.ghidra_headless and cfg.ghidra_headless.exists()),
        "XenonRecomp": bool(cfg.xenonrecomp and cfg.xenonrecomp.exists()),
        "objdiff": bool(cfg.objdiff and cfg.objdiff.exists()),
        "Agent": bool(shutil.which(cfg.agent_command.split()[0])),
    }
    for name, ok in checks.items():
        console.print(f"[{'green' if ok else 'red'}]{'OK' if ok else 'MISSING'}[/] {name}")


@app.command("functions")
def functions_cmd(config: Path = Path("harness.toml")) -> None:
    """Display functions currently known to the state database."""
    functions = db_for(config).list_functions()
    table = Table("Address", "Name", "Status", "Best", "Attempts", "Priority")
    for fn in functions:
        table.add_row(fn.address_hex, fn.name, fn.status.value, f"{fn.best_score:.2f}%",
                      str(fn.attempts), f"{priority(fn):.1f}")
    console.print(table)


@app.command()
def status(config: Path = Path("harness.toml")) -> None:
    """Show aggregate project progress and the scheduler's next target."""
    functions = db_for(config).list_functions()
    total = len(functions)
    matched = sum(f.status.value == "matched" for f in functions)
    console.print(f"Functions: {total} | Matched: {matched} | Progress: "
                  f"{(matched / total * 100 if total else 0):.2f}%")
    target = select_next(functions)
    if target:
        console.print(f"Next: {target.address_hex} {target.name} (priority {priority(target):.1f})")


if __name__ == "__main__":
    app()
