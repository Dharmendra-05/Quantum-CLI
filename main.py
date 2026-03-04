#!/usr/bin/env python3
"""
Quantum-CLI Toolkit - Main Entry Point
A terminal-based, AI-integrated physics engine.
"""

import sys
import argparse
from pathlib import Path

# Ensure core modules are in path
sys.path.insert(0, str(Path(__file__).parent))

from frontend.cli_ui import QuantumCLI
from core.ai_agent import AIAgent
from core.physics_engine import PhysicsEngine
from core.latex_generator import LaTeXGenerator


def main():
    """
    Main entry point: parse command-line arguments and launch the interactive CLI.
    """
    parser = argparse.ArgumentParser(
        description="Quantum-CLI Toolkit - AI-Integrated Physics Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--export-dir",
        type=str,
        default="assets/exports",
        help="Directory where plots and LaTeX files are saved (default: assets/exports)",
    )
    parser.add_argument(
        "--no-rich",
        action="store_true",
        help="Disable rich terminal output (fallback to plain text)",
    )
    args = parser.parse_args()

    # Create export directory if it doesn't exist
    export_path = Path(args.export_dir)
    export_path.mkdir(parents=True, exist_ok=True)

    # Initialize core components
    physics_engine = PhysicsEngine(export_dir=export_path)
    ai_agent = AIAgent(physics_engine)
    latex_gen = LaTeXGenerator(export_dir=export_path)

    # Launch CLI
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