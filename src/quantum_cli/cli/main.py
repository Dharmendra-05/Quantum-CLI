#!/usr/bin/env python3
"""
Quantum-CLI: Main Entry Point
Terminal-based, AI-integrated computational physics engine.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from quantum_cli.cli.ui import QuantumCLI
from quantum_cli.core.ai_agent import AIAgent
from quantum_cli.core.latex_generator import LaTeXGenerator
from quantum_cli.core.physics_engine import PhysicsEngine


def _configure_logging(verbose: bool = False) -> None:
    """Centralise logging config. Physics/agent modules use their own named loggers."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    """Parse CLI arguments, wire up components, and launch the interactive REPL."""
    parser = argparse.ArgumentParser(
        prog="quantum",
        description="Quantum-CLI — Terminal-First Computational Physics Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  quantum\n"
            "  quantum --export-dir ./quantum-exports\n"
            "  quantum --no-rich\n"
            "  quantum --verbose\n"
        ),
    )
    parser.add_argument(
        "--export-dir",
        type=str,
        default="quantum-exports",
        help="Directory for plots and LaTeX files (default: quantum-exports)",
    )
    parser.add_argument(
        "--no-rich",
        action="store_true",
        help="Disable Rich terminal output and fall back to plain text",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging",
    )
    args = parser.parse_args()

    _configure_logging(args.verbose)

    export_path = Path(args.export_dir).resolve()
    export_path.mkdir(parents=True, exist_ok=True)

    physics_engine = PhysicsEngine(export_dir=export_path)
    ai_agent = AIAgent(physics_engine)
    latex_gen = LaTeXGenerator(export_dir=export_path)

    cli = QuantumCLI(
        ai_agent=ai_agent,
        latex_generator=latex_gen,
        export_dir=export_path,
        use_rich=not args.no_rich,
    )

    try:
        cli.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
