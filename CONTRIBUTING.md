# Contributing to Quantum-CLI

Thank you for your interest in contributing to **Quantum-CLI**! We welcome contributions from physicists, students, software engineers, and terminal enthusiasts.

---

## 1. Code of Conduct

All contributors are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat all community members with respect and kindness.

---

## 2. Architecture & Design Rules

To ensure long-term stability and performance, Quantum-CLI adheres to strict architectural boundaries:

1. **Layer Dependency Direction:**
   ```text
   cli → commands → core
   commands → render
   ```
   `core/` must **never** import from `cli/` or `render/`. It contains pure physics, has no I/O, no printing, and no Matplotlib dependencies.

2. **Startup Performance (Lazy Imports):**
   Heavy scientific libraries (`numpy`, `scipy`, `matplotlib`, `sympy`) must be imported **inside functions** (`run()`), never at module top level. Startup latency for `--help` and `exit` must remain sub-150ms.

3. **Output Path Policy:**
   Never write inside the installed package folder. All exports must go to the user-specified directory (`--export-dir`, defaulting to `./quantum-exports`). Always display the full path of every file written.

4. **Adding New Commands:**
   Adding a command should touch only two places:
   - One command implementation file in `src/quantum_cli/commands/`
   - One `CommandSpec` declaration in `src/quantum_cli/commands/manifest.py`

---

## 3. Getting Started with Development

We recommend using [`uv`](https://github.com/astral-sh/uv) for fast, isolated development:

### 1. Fork & Clone
```bash
git clone https://github.com/Dharmendra-05/Quantum-CLI.git
cd Quantum-CLI
```

### 2. Install Development Dependencies
```bash
uv sync --extra dev
```
*(or via pip: `pip install -e ".[dev]"`)*

### 3. Run the Safety Net Tests
```bash
uv run --extra dev pytest tests/
```

### 4. Run the Linter & Formatter
```bash
uv run --with ruff ruff check src/
```

---

## 4. Pull Request Guidelines

1. **Create a Feature Branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. **Follow Conventional Commits:**
   Use standard commit prefixes:
   - `feat:` for new capabilities
   - `fix:` for bug fixes
   - `test:` for test additions or modifications
   - `docs:` for documentation updates
   - `refactor:` for internal restructuring
3. **Keep Golden Tests Green:**
   Characterization tests in `tests/golden/` must remain passing. Never alter physics results unless the PR explicitly aims to correct a documented numerical bug.
4. **Submit Your PR:**
   Push your branch and open a pull request against `main`. Provide a clear description of your changes and include sample command outputs where relevant.
