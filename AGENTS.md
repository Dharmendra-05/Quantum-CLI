# AGENTS.md: Quantum-CLI

## Rules
- Work on ONE step of IMPLEMENTATION_PLAN.md at a time. Never start the next step.
- Show a plan before editing multiple files. Wait for approval.
- Never change physics results unless the task says so. Golden tests in tests/golden must stay green.
- Dependency rule: cli → commands → core; core imports nothing from other layers.
- core/ has no I/O, no printing, no Rich, no Matplotlib.
- Heavy libraries (numpy, scipy, matplotlib, sympy) are imported inside functions, not at module top level.
- Never write inside the installed package folder. Use paths from config/paths.py.
- New command = one file in commands/ + one CommandSpec in commands/manifest.py. Nothing else.
- Type hints on public functions. Run ruff and pytest before finishing.
- Conventional Commits. One commit per step.
- Do not publish, tag, or push without asking me.
