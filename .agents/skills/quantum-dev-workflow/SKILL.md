---
name: quantum-dev-workflow
description: >-
  Standard development, benchmarking, and verification workflow for Quantum-CLI
  following the Step 1-10 incremental implementation plan.
---

# Quantum-CLI Development Workflow

## Overview
This skill provides automated guidance and testing protocols for developing, refactoring, and verifying features in `quantum-origin-cli` (`quantum`). It strictly enforces the rules from `AGENTS.md` and the 10-step reference architecture in `IMPLEMENTATION_PLAN.md`.

## Dependencies
- `uv` (for isolated package runs and fast dependency caching)
- `pytest` (for characterization and regression tests)

## Quick Start

### 1. Run the Golden Safety Net
Execute all characterization tests locking physics and agent behavior:
```bash
uv run --with "numpy>=1.24" --with "scipy>=1.11" --with "matplotlib>=3.7" --with "sympy>=1.12" --with "rich>=13.0" --with "pytest" pytest tests/
```

### 2. Measure Startup Latency
Profile `main.py` (or `quantum` entry point) startup wall-clock time:
```powershell
1..5 | ForEach-Object { (Measure-Command { uv run --with "numpy>=1.24" --with "scipy>=1.11" --with "matplotlib>=3.7" --with "sympy>=1.12" --with "rich>=13.0" python main.py --help *>$null }).TotalMilliseconds }
```

## Workflow

### Step Progression Checklist
1. **Rule Zero:** Work on ONE step of `IMPLEMENTATION_PLAN.md` at a time.
2. **Architecture Boundary:** `cli → commands → core`. `core/` must never import Rich, Matplotlib, or UI components.
3. **Lazy Imports:** Heavy scientific libraries (`numpy`, `scipy`, `matplotlib`, `sympy`) must be imported inside execution functions (`run()`), never at top level.
4. **Command Registration:** Every new command touches exactly two locations:
   - One command implementation file in `commands/`
   - One `CommandSpec` declaration in `commands/manifest.py`
5. **Output Path Policy:** All user-facing exports write to `--out` (default `./quantum-exports`). Always print the absolute path of every generated artifact.

## Common Mistakes
- **Importing Matplotlib at module root:** Causes a 780ms startup penalty and loads 75MB into memory on `--help`.
- **Modifying physics formulas during refactoring:** Always ensure `tests/golden` passes before and after code changes.
- **Scanning filesystem for plugins:** Use Python entry points (`importlib.metadata`) instead of filesystem scanning to avoid startup import penalties and wheel packaging bugs.
