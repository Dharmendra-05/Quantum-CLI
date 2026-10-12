"""
CLI User Interface Module
=========================
Premium terminal experience powered by the Rich library.

Design highlights
-----------------
- Gradient ASCII banner wrapped in a styled Panel
- console.status() spinners while the physics engine runs
- Results rendered in colour-coded Panels with data Tables
- _show_help() called directly for 'help' (no plain-text fallback)
- console.print_exception() for unexpected runtime errors
- All console access guarded for --no-rich plain-text mode
"""

import re
import traceback
from pathlib import Path
from typing import Any

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from quantum_cli import __version__ as _VERSION
from quantum_cli.core.ai_agent import AIAgent
from quantum_cli.core.latex_generator import LaTeXGenerator

# ── ASCII art banner ───────────────────────────────────────────────────────────
_BANNER_ART = r"""
   ██████  ██    ██  █████  ███    ██ ████████ ██    ██ ███    ███
  ██    ██ ██    ██ ██   ██ ████   ██    ██    ██    ██ ████  ████
  ██    ██ ██    ██ ███████ ██ ██  ██    ██    ██    ██ ██ ████ ██
  ██ ▄▄ ██ ██    ██ ██   ██ ██  ██ ██    ██    ██    ██ ██  ██  ██
   ██████   ██████  ██   ██ ██   ████    ██     ██████  ██      ██
      ▀▀
  ██████ ██      ██
 ██      ██      ██
 ██      ██      ██
 ██      ██      ██
  ██████ ███████ ██
"""

_BANNER_GRADIENT = [
    "bold bright_cyan",
    "bold cyan",
    "bold #58a6ff",
    "bold #79c0ff",
    "bold bright_cyan",
    "bold cyan",
    "bold #58a6ff",
    "bold #79c0ff",
    "bold bright_cyan",
    "bold cyan",
    "bold #58a6ff",
]

_TAGLINE = f"⚛  AI-Integrated Physics Engine  ·  v{_VERSION}"

# ── Helpers ────────────────────────────────────────────────────────────────────

def _strip_markup(text: str) -> str:
    """Remove Rich markup tags for plain-text fallback output."""
    return re.sub(r"\[/?[^\]]*\]", "", text)


class QuantumCLI:
    """
    Premium interactive REPL for the Quantum-CLI Toolkit.

    Data-flow
    ---------
    run()  →  _process_command()
                 ├─ ai.parse()           (instant, no spinner)
                 ├─ _show_help()         (for 'help')
                 ├─ console.status()     (spinner while ai.execute() runs)
                 ├─ _display_ho_result() / _display_kss_result()
                 └─ _offer_latex()
    """

    def __init__(
        self,
        ai_agent: AIAgent,
        latex_generator: LaTeXGenerator,
        export_dir: Path,
        use_rich: bool = True,
    ) -> None:
        self.ai         = ai_agent
        self.latex      = latex_generator
        self.export_dir = export_dir
        self.use_rich   = use_rich
        # highlight=False prevents Rich from auto-styling numbers / strings in
        # output — gives us full control over the look of every printed line.
        self.console    = Console(highlight=False) if use_rich else None
        self.running    = True

    # ── Generic output helpers ─────────────────────────────────────────────────

    def _print(self, markup: str) -> None:
        """Print a Rich-markup string (strips tags in plain-text mode)."""
        if self.use_rich:
            self.console.print(markup)
        else:
            print(_strip_markup(markup))

    def _rule(self, title: str = "") -> None:
        if self.use_rich:
            self.console.print(Rule(title, style="dim #30363d"))

    # ── UI components ──────────────────────────────────────────────────────────

    def _show_banner(self) -> None:
        if not self.use_rich:
            print("=" * 60)
            print("  Quantum-CLI Toolkit — AI-Integrated Physics Engine")
            print(f"  v{_VERSION}")
            print("=" * 60)
            print("  Type 'help' for commands, 'exit' to quit.\n")
            return

        # Build gradient banner text line-by-line
        banner_text = Text(justify="center")
        for i, line in enumerate(_BANNER_ART.strip("\n").split("\n")):
            style = _BANNER_GRADIENT[i % len(_BANNER_GRADIENT)]
            banner_text.append(line + "\n", style=style)

        self.console.print()
        self.console.print(
            Panel(
                Align.center(banner_text),
                border_style="#21262d",
                padding=(0, 6),
                subtitle=Text(_TAGLINE, style="dim cyan"),
            )
        )
        self.console.print(
            Align.center(
                Text.from_markup(
                    "  Type  [bold cyan]help[/bold cyan]  for commands  ·  "
                    "[bold cyan]exit[/bold cyan]  to quit  ",
                    style="dim",
                )
            )
        )
        self.console.print()

    def _show_help(self) -> None:
        if not self.use_rich:
            print(
                "\nCommands:\n"
                "  harmonic oscillator n=N             "
                "QHO wavefunction  (0 \u2264 N \u2264 15)\n"
                "  harmonic oscillator n=N range A to B "
                "custom x-range in natural units\n"
                "  harmonic oscillator states N1,N2,... "
                "multi-eigenstate potential-well plot\n"
                "  kss bound                            "
                "KSS universal viscosity bound\n"
                "  kss bound with sample data           "
                "same + hypothetical QGP data\n"
                "  cyclotron [B=..] [voltage=..] [radius=..] "
                "Lorentz force particle accelerator\n"
                "  help                                 "
                "this message\n"
                "  exit / quit                          "
                "exit the application\n"
            )
            return

        table = Table(
            title="Available Commands",
            title_style="bold #79c0ff",
            show_header=True,
            header_style="bold #8b949e",
            border_style="#30363d",
            box=box.ROUNDED,
            padding=(0, 1),
            expand=False,
        )
        table.add_column("Command",      style="bold cyan",   no_wrap=True, min_width=38)
        table.add_column("Description",  style="#c9d1d9",     min_width=46)
        table.add_column("Example",      style="dim #8b949e", min_width=36)

        table.add_row(
            "harmonic oscillator n=[italic]N[/italic]",
            "Compute ψ_n(x) and |ψ_n(x)|² for level N  (0 ≤ N ≤ 15).",
            "harmonic oscillator n=3",
        )
        table.add_row(
            "harmonic oscillator n=[italic]N[/italic]"
            " range [italic]A[/italic] to [italic]B[/italic]",
            "Same, with a custom x-range in natural units (x / x₀).",
            "harmonic oscillator n=5 range -8 to 8",
        )
        table.add_row(
            "harmonic oscillator states [italic]N1,N2,...[/italic]",
            "Multi-eigenstate dual-panel potential-well plot.",
            "harmonic oscillator states 0,1,2,3",
        )
        table.add_row(
            "kss bound",
            "Compute η/s ≥ ħ/(4πk_B) — the KSS viscosity bound.",
            "show kss bound",
        )
        table.add_row(
            "kss bound with sample data",
            "Same, overlaying illustrative QGP data on the plot.",
            "kss bound with sample data",
        )
        table.add_row(
            "cyclotron [italic]B=1.5 voltage=50kV radius=0.5m[/italic]",
            "DOP853 Lorentz force simulation & dual-panel orbit plot.",
            "cyclotron B=1.5 voltage=60kV radius=60cm",
        )
        table.add_row("help",  "Display this help table.",  "help")
        table.add_row("exit",  "Exit the application.",     "exit")

        self.console.print()
        self.console.print(Align.center(table))
        self.console.print()

    # ── Result display panels ──────────────────────────────────────────────────

    def _display_ho_result(self, data: dict[str, Any]) -> None:
        """Render QHO results in a colour-coded Panel with a data Table."""
        n          = data["n"]
        energy     = data["energy"]
        energy_nat = data["energy_nat"]
        x_tp       = data["x_tp"]
        x_range    = data.get("x_range")
        plot_path  = data.get("plot_path")

        if not self.use_rich:
            print(f"\n  n = {n}")
            print(f"  Energy   : {energy:.6e} J  ({energy_nat:.1f} \u0127\u03c9)")
            print(f"  x_tp     : \u00b1{x_tp:.4f} x\u2080")
            if plot_path:
                print(f"  Plot     : {plot_path}")
            return

        tbl = Table(
            show_header=False, box=box.SIMPLE,
            padding=(0, 2), show_edge=False,
        )
        tbl.add_column("Key",   style="bold #79c0ff", no_wrap=True)
        tbl.add_column("Value", style="bright_white")

        tbl.add_row("Quantum level",  f"n = {n}")
        tbl.add_row("Energy (SI)",    f"{energy:.6e} J")
        tbl.add_row("Energy (nat.)",  f"{energy_nat:.1f} ħω")
        tbl.add_row("Classical x_tp", f"±{x_tp:.4f} x₀   [dim](x₀ = √(ħ/mω))[/dim]")
        if x_range:
            tbl.add_row(
                "Plot x-range",
                f"[{x_range[0]:.2f}, {x_range[1]:.2f}] x₀  (natural units)",
            )
        if plot_path:
            tbl.add_row("Plot saved", f"[dim]{plot_path}[/dim]")

        self.console.print(
            Panel(
                tbl,
                title="[bold #3fb950]✔  Quantum Harmonic Oscillator[/bold #3fb950]",
                border_style="#3fb950",
                padding=(1, 2),
            )
        )

    def _display_multi_ho_result(self, data: dict[str, Any]) -> None:
        """Render multi-eigenstate QHO results in a styled table inside a Panel."""
        states = data["states"]
        x_range = data.get("x_range")
        plot_path = data.get("plot_path")

        if not self.use_rich:
            print("\n  Quantum Harmonic Oscillator - Multi-Eigenstates:")
            for s in states:
                print(
                    f"    n = {s['n']}: E = {s['energy']:.6e} J ({s['energy_nat']:.1f} hbar*omega), "
                    f"x_tp = +/-{s['x_tp']:.4f} x_0"
                )
            if plot_path:
                print(f"  Plot : {plot_path}")
            return

        table = Table(
            box=box.SIMPLE_HEAVY,
            header_style="bold #79c0ff",
            border_style="#30363d",
            padding=(0, 2),
        )
        table.add_column("Level (n)", justify="center", style="bold #58a6ff")
        table.add_column("Energy (SI)", justify="right", style="bright_white")
        table.add_column("Energy (nat.)", justify="right", style="#3fb950")
        table.add_column("Classical Turning Point (±x_tp)", justify="right", style="#d29922")

        for s in states:
            table.add_row(
                f"n = {s['n']}",
                f"{s['energy']:.6e} J",
                f"{s['energy_nat']:.1f} ħω",
                f"±{s['x_tp']:.4f} x₀",
            )

        details = Text()
        if x_range:
            details.append(f"Grid range: [{x_range[0]:.2f}, {x_range[1]:.2f}] x₀\n", style="dim")
        if plot_path:
            details.append("Dual-panel potential-well plot saved:\n", style="bold #79c0ff")
            details.append(f"{plot_path}", style="dim underline")

        content = Table.grid(padding=1)
        content.add_row(table)
        content.add_row(details)

        self.console.print(
            Panel(
                content,
                title="[bold #3fb950]✔  QHO Multi-Eigenstate Visualizer[/bold #3fb950]",
                border_style="#3fb950",
                padding=(1, 2),
            )
        )

    def _display_kss_result(self, data: dict[str, Any]) -> None:
        """Render KSS bound results in a colour-coded Panel with a data Table."""
        bound     = data["bound_value"]
        plot_path = data.get("plot_path")

        if not self.use_rich:
            print(f"\n  η/s ≥ ħ/(4πk_B) = {bound:.6e} K·s")
            if plot_path:
                print(f"  Plot : {plot_path}")
            return

        tbl = Table(
            show_header=False, box=box.SIMPLE,
            padding=(0, 2), show_edge=False,
        )
        tbl.add_column("Key",   style="bold #79c0ff", no_wrap=True)
        tbl.add_column("Value", style="bright_white")

        tbl.add_row("Bound  η/s ≥",   f"{bound:.6e} K·s")
        tbl.add_row("Formula",         "ħ / (4π k_B)")
        tbl.add_row("Physical system", "Quark-Gluon Plasma (QGP)")
        tbl.add_row("Reference",       "Kovtun, Son & Starinets (2005)")
        if plot_path:
            tbl.add_row("Plot saved", f"[dim]{plot_path}[/dim]")

        self.console.print(
            Panel(
                tbl,
                title="[bold #d29922]✔  KSS Viscosity Bound[/bold #d29922]",
                border_style="#d29922",
                padding=(1, 2),
            )
        )

    def _display_cyclotron_result(self, data: dict[str, Any]) -> None:
        """Render cyclotron simulation results in a colour-coded Panel with a data Table."""
        particle = data.get("particle", "proton")
        b_field_t = data.get("B_field", 1.5)
        dee_voltage_v = data.get("gap_voltage", 50000.0)
        f_c_mhz = data.get("cyclotron_frequency_mhz", 0.0)
        omega_c = data.get("omega_c", 0.0)
        omega_c_mrad = (omega_c / 1e6) if omega_c > 1000 else omega_c
        final_energy_mev = data.get("final_energy_mev", 0.0)
        exit_radius_cm = data.get("final_radius_cm", 0.0)
        max_radius_m = data.get("dee_radius", 0.5)
        turns = data.get("turns", 0.0)
        t_final_us = data.get("flight_time_us", 0.0)
        plot_path = data.get("plot_path")

        if not self.use_rich:
            print("\n  Cyclotron Particle Accelerator Simulation:")
            print(f"    Particle         : {str(particle).capitalize()}")
            print(f"    Magnetic Field B : {b_field_t:.3f} T")
            print(f"    Dee Voltage V_0  : {dee_voltage_v / 1e3:.1f} kV")
            print(f"    Resonance Freq   : {f_c_mhz:.3f} MHz (omega = {omega_c_mrad:.3f} Mrad/s)")
            print(f"    Final Energy     : {final_energy_mev:.3f} MeV")
            print(f"    Exit Radius      : {exit_radius_cm:.2f} cm (Dee max: {max_radius_m * 100:.1f} cm)")
            print(f"    Turns / Duration : ~{turns:.1f} turns ({t_final_us:.2f} us)")
            if plot_path:
                print(f"    Plot             : {plot_path}")
            return

        tbl = Table(
            show_header=False, box=box.SIMPLE,
            padding=(0, 2), show_edge=False,
        )
        tbl.add_column("Key", style="bold #79c0ff", no_wrap=True)
        tbl.add_column("Value", style="bright_white")

        tbl.add_row("Accelerated particle", str(particle).capitalize())
        tbl.add_row("Magnetic field (B)", f"{b_field_t:.3f} T")
        tbl.add_row("Peak Dee voltage (V₀)", f"{dee_voltage_v / 1e3:.1f} kV")
        tbl.add_row("Resonance frequency (f_c)", f"{f_c_mhz:.3f} MHz  [dim](ω_c = {omega_c_mrad:.3f} Mrad/s)[/dim]")
        tbl.add_row("Final kinetic energy (E_k)", f"{final_energy_mev:.3f} MeV")
        tbl.add_row("Exit radius / Dee radius", f"{exit_radius_cm:.2f} cm / {max_radius_m * 100:.1f} cm")
        tbl.add_row("Completed revolutions", f"~{turns:.1f} turns  [dim](elapsed {t_final_us:.2f} µs)[/dim]")
        if plot_path:
            tbl.add_row("Plot saved", f"[dim]{plot_path}[/dim]")

        self.console.print(
            Panel(
                tbl,
                title="[bold #3fb950]✔  Cyclotron Particle Accelerator[/bold #3fb950]",
                border_style="#3fb950",
                padding=(1, 2),
            )
        )

    def _display_error(self, message: str) -> None:
        """Render an error in a red Panel (or plain text in --no-rich mode)."""
        if not self.use_rich:
            print(f"\nERROR: {_strip_markup(message)}")
            return

        self.console.print(
            Panel(
                Text(message, style="#f85149"),
                title="[bold #f85149]✖  Error[/bold #f85149]",
                border_style="#f85149",
                padding=(0, 2),
            )
        )

    # ── Command pipeline ───────────────────────────────────────────────────────

    def _process_command(self, user_input: str) -> None:
        """
        Full command pipeline:

        1. parse()        — instant, no spinner
        2. route special  — 'exit' / 'help' handled immediately
        3. execute()      — heavy work runs under console.status() spinner
        4. display result — Panel + Table in rich mode, plain text otherwise
        5. offer LaTeX    — optional export prompt
        """
        # ── 1. Parse ──────────────────────────────────────────────────────────
        parsed = self.ai.parse(user_input)

        # ── 2. Special routes ─────────────────────────────────────────────────
        if parsed["action"] == "exit":
            self.running = False
            return

        if parsed["action"] == "help":
            self._show_help()
            return

        # ── 3. Execute with spinner ───────────────────────────────────────────
        spinner_label = {
            "harmonic_oscillator":       "[bold cyan]⚛  Solving Schrödinger equation…",
            "harmonic_oscillator_multi": "[bold cyan]⚛  Computing multi-eigenstate wavefunctions…",
            "kss_bound":                 "[bold yellow]⚛  Computing viscosity bound…",
            "cyclotron":                 "[bold cyan]⚛  Simulating particle acceleration (DOP853)…",
        }.get(parsed["action"], "[bold cyan]⚛  Processing…")

        if self.use_rich:
            with self.console.status(spinner_label, spinner="dots"):
                result = self.ai.execute(parsed)
        else:
            result = self.ai.execute(parsed)

        # ── 4. Display result ─────────────────────────────────────────────────
        self._rule()

        if result["success"]:
            data = result.get("data")
            action = parsed["action"]

            if action == "harmonic_oscillator" and data:
                self._display_ho_result(data)
            elif action == "harmonic_oscillator_multi" and data:
                from quantum_cli.render.qho_plot import plot_multi_eigenstates

                states_str = "_".join(str(s["n"]) for s in data["states"])
                plot_file = self.export_dir / f"qho_multi_eigenstates_{states_str}.png"
                plot_multi_eigenstates(data, save_path=plot_file)
                data["plot_path"] = str(plot_file)
                self._display_multi_ho_result(data)
            elif action == "kss_bound" and data:
                self._display_kss_result(data)
            elif action == "cyclotron" and data:
                from quantum_cli.render.cyclotron_plot import plot_cyclotron_trajectory

                plot_file = self.export_dir / "cyclotron_trajectory.png"
                plot_cyclotron_trajectory(data, save_path=plot_file)
                data["plot_path"] = str(plot_file)
                self._display_cyclotron_result(data)
            else:
                # Fallback for any success without structured data
                self._print(
                    f"[bold #3fb950]✔[/bold #3fb950]  {result['message']}"
                )
        else:
            self._display_error(result["message"])

        # ── 5. Optional LaTeX export ──────────────────────────────────────────
        if result["success"] and result.get("data"):
            self._offer_latex(parsed["action"], result["data"])

        self._rule()

    # ── LaTeX export ───────────────────────────────────────────────────────────

    def _offer_latex(self, action: str, data: dict[str, Any]) -> None:
        """Prompt the user and, if confirmed, generate a .tex file."""
        if not self.use_rich:
            resp = input("\nGenerate LaTeX report? [y/N]: ").strip().lower()
            if resp == "y":
                path = self._run_latex_generation(action, data)
                if path:
                    print(f"LaTeX saved: {path}")
            return

        resp = Prompt.ask(
            "\n  [dim]Generate LaTeX report?[/dim]",
            choices=["y", "n"],
            default="n",
            show_default=True,
        )
        if resp != "y":
            return

        with self.console.status("[bold cyan]⚛  Generating LaTeX…", spinner="dots"):
            path = self._run_latex_generation(action, data)

        if path:
            self.console.print(
                f"\n  [bold #3fb950]📄  LaTeX saved →[/bold #3fb950]"
                f" [dim cyan]{path}[/dim cyan]"
            )

    def _run_latex_generation(
        self, action: str, data: dict[str, Any]
    ) -> Path | None:
        """Call the LaTeX generator and return the saved path (or None on error)."""
        try:
            if action == "harmonic_oscillator":
                return self.latex.generate_and_save(
                    "harmonic_oscillator",
                    n=data["n"],
                    energy=data["energy"],
                )
            if action == "harmonic_oscillator_multi":
                return self.latex.generate_and_save(
                    "harmonic_oscillator_multi",
                    states=[s["n"] for s in data["states"]],
                    state_records=data["states"],
                )
            if action == "kss_bound":
                return self.latex.generate_and_save(
                    "kss_bound",
                    bound_value=data["bound_value"],
                )
            if action == "cyclotron":
                return self.latex.generate_and_save("cyclotron", **data)
        except Exception as exc:
            self._display_error(f"LaTeX generation failed: {exc}")
        return None

    # ── Main REPL ──────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Main REPL loop."""
        self._show_banner()

        while self.running:
            try:
                if self.use_rich:
                    user_input: str = Prompt.ask(
                        "\n[bold #58a6ff]quantum[/bold #58a6ff]"
                        "[bold dim #30363d]❯[/bold dim #30363d]"
                    )
                else:
                    user_input = input("\nquantum> ")

                if not user_input.strip():
                    continue

                self._process_command(user_input.strip())

            except KeyboardInterrupt:
                if self.use_rich:
                    self.console.print()
                    self.console.print("[bold yellow]👋  Goodbye![/bold yellow]")
                else:
                    print("\nGoodbye!")
                break

            except EOFError:
                # Handles piped input / non-interactive sessions gracefully
                break

            except Exception:
                if self.use_rich:
                    self.console.print_exception(show_locals=False)
                else:
                    traceback.print_exc()

        self._print("\n[dim]Quantum-CLI terminated.[/dim]")
