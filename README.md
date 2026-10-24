# XenonHarness

XenonHarness is a provider-independent orchestration layer for AI-assisted Xbox 360 reverse engineering. It is designed for binaries you own or are authorized to analyze.

The project deliberately separates **reasoning** from **verification**: an AI coding agent proposes source changes, while deterministic tools build, diff, score, persist state, and decide what should be attempted next.

## Architecture

```text
XEX -> Ghidra/headless analysis -> evidence packages -> scheduler -> coding agent
                                                          |          |
                                                          |          v
                                                          |       source edit
                                                          |          |
                                                          |          v
                                                          +---- build + objdiff
                                                                     |
                                                               score / diff
                                                                     |
                                                           retry or mark matched
```

Two workflows are planned:

- **decomp**: human-readable C/C++ reconstruction with compiler/objdiff feedback.
- **recomp**: XenonRecomp-backed static recompilation orchestration and runtime bring-up.

## Current foundation

The initial implementation includes:

- Python 3.11+ CLI package.
- TOML configuration.
- SQLite function/attempt state.
- Evidence-oriented function scheduler.
- Provider-independent agent command adapter.
- Dependency doctor, status, and function-list commands.
- Autonomous worker contract with anti-cheating verification rules.
- Git exclusions for XEX/ISO/input data.

The next implementation slice is Ghidra headless export, evidence-package generation, objdiff parsing, and the full orchestrator loop.

## Install

```powershell
# Clone your repository, then from its root:
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item harness.example.toml harness.toml
```

Edit `harness.toml` with your local tool paths. Put your own `default.xex` under `input/` or point the configuration to an external path. The `input/` directory and `*.xex`/`*.iso` are ignored by Git.

```powershell
xenonharness doctor
xenonharness status
xenonharness functions
```

## Design principles

1. **The model is replaceable.** Codex, Claude Code, or another coding agent is an adapter, not the architecture.
2. **Verification is authoritative.** Models never decide that their own output matches.
3. **Persistent knowledge.** Attempts and scores survive restarts; later work can reuse discoveries.
4. **Evidence over hallucination.** Function context is generated from static analysis and prior verified work.
5. **Easy functions first.** The scheduler prioritizes tractable work and near matches to accumulate knowledge quickly.
6. **Game material stays local.** Do not commit XEX files, ISOs, extracted assets, or other copyrighted game content.

## Roadmap

- Ghidra headless importer/export scripts for functions, PPC disassembly, decompiler output, xrefs, strings and call graph.
- Normalized evidence JSON format.
- objdiff CLI integration and machine-readable match scoring.
- Compiler/build adapters.
- XenonRecomp adapter.
- Attempt worktrees and automatic rollback on regressions.
- Full `analyze`, `run`, and `run --function` commands.
- Symbol/type knowledge base.
- Regression verification across previously matched functions.
- Codex and Claude wrapper examples.
- Tests and Windows bootstrap script.

## Legal scope

Use XenonHarness only on software you own or have permission to reverse engineer, and follow applicable law and license terms. The repository should contain harness code and clean-room reconstruction work—not copyrighted game binaries or assets.
