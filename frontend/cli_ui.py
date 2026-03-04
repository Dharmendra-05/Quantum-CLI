"""
CLI User Interface Module
Uses the Rich library to create a beautiful terminal interface.
"""

import sys
from pathlib import Path
from typing import Optional
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich import print as rprint

from core.ai_agent import AIAgent
from core.latex_generator import LaTeXGenerator


class QuantumCLI:
    """
    Main interactive CLI class.
    """

    def __init__(
        self,
        ai_agent: AIAgent,
        latex_generator: LaTeXGenerator,
        export_dir: Path,
        use_rich: bool = True,
    ):
        self.ai = ai_agent
        self.latex = latex_generator
        self.export_dir = export_dir
        self.use_rich = use_rich
        self.console = Console() if use_rich else None
        self.running = True

    def _print(self, text: str, style: str = "default"):
        """Print text, using Rich if available."""
        if self.use_rich:
            self.console.print(text, style=style)
        else:
            print(text)

    def _show_banner(self):
        """Display the startup banner."""
        banner = r"""
   ▄████████  █    ██  ▄█   ▄█          ▄████████  ▄█               ██     ███    █▄
  ███    ███  ██  ███  ██  ███         ███    ███ ███           ▀█████████▄ ███    ███
  ███    █▀   ██  ███  ███▌ ███         ███    █▀  ███              ▀███▀▀██ ███    ███
  ███         ██  ███  ███▌ ███        ▄███▄▄▄     ███               ███   ▀ ███    ███
▀███████████  ██  ███  ███▌ ███       ▀▀███▀▀▀     ███               ███     ███    ███
         ███  ██  ███  ███  ███         ███    █▄  ███               ███     ███    ███
   ▄█    ███  ██  ███  ███  ███▌    ▄   ███    ███ ███▌    ▄         ███     ███    ███
 ▄████████▀   ██████   █▀   █████▄▄██   ██████████ █████▄▄██        ▄████▀   ████████▀
                            ▀                                  ▀
        """
        if self.use_rich:
            self.console.print(banner, style="bold cyan")
            self.console.print(
                "Welcome to the Quantum-CLI Toolkit - AI-Integrated Physics Engine",
                style="bold green",
            )
            self.console.print("Type 'help' for commands, 'exit' to quit.\n", style="yellow")
        else:
            print(banner)
            print("Welcome to the Quantum-CLI Toolkit")
            print("Type 'help' for commands, 'exit' to quit.\n")

    def _show_help(self):
        """Display help information in a Rich table."""
        if not self.use_rich:
            print("Available commands: help, exit, harmonic oscillator, kss bound")
            return

        table = Table(title="Available Commands", show_header=True, header_style="bold magenta")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Example", style="white")

        table.add_row(
            "harmonic oscillator",
            "Compute wavefunction and probability density for a given level n.",
            "harmonic oscillator n=2",
        )
        table.add_row(
            "kss bound",
            "Display the KSS bound (η/s) for QGP, with optional sample data.",
            "show KSS bound with sample data",
        )
        table.add_row("help", "Show this help message.", "help")
        table.add_row("exit", "Exit the application.", "exit")

        self.console.print(table)

    def _process_command(self, user_input: str):
        """
        Process a single user command with a spinner.
        """
        if self.use_rich:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Thinking...", total=None)
                # Simulate AI processing delay
                time.sleep(0.3)
                parsed = self.ai.parse(user_input)
                result = self.ai.execute(parsed)
        else:
            parsed = self.ai.parse(user_input)
            result = self.ai.execute(parsed)

        # Handle exit
        if parsed["action"] == "exit":
            self.running = False
            return

        # Display result
        if result["success"]:
            self._print(f"✅ {result['message']}", style="bold green")
            # Optionally generate LaTeX
            if parsed["action"] in ("harmonic_oscillator", "kss_bound") and result.get("data"):
                self._generate_latex(parsed["action"], result["data"])
        else:
            self._print(f"❌ {result['message']}", style="bold red")

    def _generate_latex(self, action: str, data: dict):
        """
        Ask user if they want LaTeX output and generate if yes.
        """
        if not self.use_rich:
            # Simple prompt
            resp = input("Generate LaTeX report? (y/n): ").strip().lower()
            if resp == "y":
                if action == "harmonic_oscillator":
                    path = self.latex.generate_and_save(
                        "harmonic_oscillator", n=data["n"], energy=data["energy"]
                    )
                elif action == "kss_bound":
                    path = self.latex.generate_and_save(
                        "kss_bound", bound_value=data["bound_value"]
                    )
                else:
                    return
                if path:
                    print(f"LaTeX saved to: {path}")
            return

        # Rich prompt
        resp = Prompt.ask("Generate LaTeX report?", choices=["y", "n"], default="n")
        if resp == "y":
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Generating LaTeX...", total=None)
                time.sleep(0.5)
                if action == "harmonic_oscillator":
                    path = self.latex.generate_and_save(
                        "harmonic_oscillator", n=data["n"], energy=data["energy"]
                    )
                elif action == "kss_bound":
                    path = self.latex.generate_and_save("kss_bound", bound_value=data["bound_value"])
                else:
                    path = None
            if path:
                self.console.print(f"📄 LaTeX saved to: [bold cyan]{path}[/bold cyan]")

    def run(self):
        """
        Main REPL loop.
        """
        self._show_banner()

        while self.running:
            try:
                if self.use_rich:
                    user_input = Prompt.ask("[bold blue]quantum>[/bold blue]")
                else:
                    user_input = input("quantum> ")

                if not user_input.strip():
                    continue

                self._process_command(user_input)

            except KeyboardInterrupt:
                self._print("\n👋 Goodbye!", style="bold yellow")
                break
            except Exception as e:
                self._print(f"Unexpected error: {e}", style="bold red")
                if not self.use_rich:
                    import traceback

                    traceback.print_exc()

        self._print("Quantum-CLI terminated.", style="dim")