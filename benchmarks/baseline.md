# Quantum-CLI Baseline Benchmarks (Step 1)

> **Measurement Date:** 2026-10-12  
> **Target Command:** `python main.py --help`  
> **Environment:** Python 3.13.13 (CPython, Windows x86_64)  
> **Git Commit:** `04be9b7` (pre-refactoring baseline)

---

## 1. Startup Latency

Five consecutive runs measuring wall-clock duration for displaying the help menu:

| Run | Duration (ms) | Duration (s) |
|---|---|---|
| **Run 1** | 2,929.7 ms | 2.93 s |
| **Run 2** | 2,234.6 ms | 2.23 s |
| **Run 3** | 2,260.3 ms | 2.26 s |
| **Run 4** | 2,535.9 ms | 2.54 s |
| **Run 5** | 3,903.7 ms | 3.90 s |
| **Average** | **2,772.8 ms** | **2.77 s** |

---

## 2. Memory Consumption

- **Peak Traced Python Memory:** `75.05 MB`

---

## 3. Profiling & Root Cause Analysis

- Top-level import chain in `main.py`:
  - `main.py` → `frontend.cli_ui` → `core.latex_generator` (`sympy`)
  - `main.py` → `frontend.cli_ui` → `core.physics_engine` (`numpy`, `scipy`, `matplotlib`)
- Heavy scientific library imports alone consume **780.9 ms** and allocate **>70 MB** before argument parsing starts.

---

## 4. Step 5 Target Gate

- By implementing lazy imports inside command handlers (`run()`) and using a lightweight static `CommandSpec` manifest, `--help` and `exit` must execute **without** loading `numpy`, `scipy`, `matplotlib`, or `sympy`.
- **Target Startup Time:** `< 150 ms`
- **Target Memory for Help:** `< 15 MB`
