"""
LaTeX Generator Module
======================
Produces standalone .tex documents for physics results.
Uses SymPy for symbolic expression rendering.
"""

import logging
from pathlib import Path
from typing import Any

import sympy as sp
from sympy import latex as sp_latex

logger = logging.getLogger(__name__)


def _format_sci_latex(val: float, precision: int = 6) -> str:
    """Format a floating-point number in standard LaTeX scientific notation (e.g. 1.23 \times 10^{-4})."""
    s = f"{val:.{precision}e}"
    base, exp = s.split("e")
    exp_int = int(exp)
    if exp_int == 0:
        return f"{float(base):.{precision}f}".rstrip("0").rstrip(".")
    return f"{base} \\times 10^{{{exp_int}}}"


class LaTeXGenerator:
    """
    Generates and saves LaTeX documents for QHO, KSS, and Cyclotron results.
    """

    def __init__(self, export_dir: Path) -> None:
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _save_tex(self, content: str, filename: str) -> Path:
        """Write *content* to <export_dir>/<filename>.tex and return the path."""
        filepath = self.export_dir / f"{filename}.tex"
        filepath.write_text(content, encoding="utf-8")
        logger.info("LaTeX saved → %s", filepath)
        return filepath

    @staticmethod
    def _preamble(title: str) -> str:
        """Return a minimal but complete LaTeX preamble."""
        return (
            r"\documentclass{article}" + "\n"
            r"\usepackage[utf8]{inputenc}" + "\n"
            r"\usepackage{amsmath, amssymb}" + "\n"
            r"\usepackage[a4paper, margin=1in]{geometry}" + "\n"
            r"\usepackage{hyperref}" + "\n\n"
            rf"\title{{{title}}}" + "\n"
            r"\author{Quantum-CLI Toolkit}" + "\n"
            r"\date{\today}" + "\n"
        )

    # ── Document generators ───────────────────────────────────────────────────

    def harmonic_oscillator_tex(self, n: int, energy: float) -> str:
        """
        Full LaTeX document for QHO level n.

        Parameters
        ----------
        n      : Quantum number.
        energy : Energy eigenvalue in Joules.
        """
        x = sp.Symbol("x", real=True)
        try:
            H_n     = sp.hermite(n, x)
            psi_sym = H_n * sp.exp(-x ** 2 / 2)
            psi_tex = sp_latex(psi_sym)
        except Exception:
            logger.warning("SymPy failed to evaluate H_%d; using placeholder.", n)
            psi_tex = r"H_{n}(x)\,e^{-x^2/2}"

        e_nat  = n + 0.5
        x_tp   = sp.sqrt(2 * n + 1)
        e_si_tex = _format_sci_latex(energy)

        doc = self._preamble("Quantum Harmonic Oscillator Results")
        doc += rf"""
\begin{{document}}
\maketitle

\section{{Energy Level $n = {n}$}}

The energy eigenvalue is
\[
  E_{{{n}}} = \hbar\omega\!\left({n} + \tfrac{{1}}{{2}}\right)
            = {e_nat}\,\hbar\omega
            = {e_si_tex}~\text{{J}}.
\]

\section{{Wavefunction in Natural Units ($\hbar = m = \omega = 1$)}}

With the dimensionless coordinate $x$ expressed in units of
$x_0 = \sqrt{{\hbar/m\omega}}$, the normalised wavefunction is
\[
  \psi_{{{n}}}(x)
  = \frac{{1}}{{\sqrt{{\sqrt{{\pi}}\,2^{{{n}}}\,{n}!}}}}
    \,H_{{{n}}}(x)\,e^{{-x^2/2}},
\]
where $H_{{{n}}}$ is the physicists' Hermite polynomial of degree ${n}$.
Explicitly:
\[
  \psi_{{{n}}}(x) \;\propto\; {psi_tex}.
\]

The classical turning points satisfy $E_n = \tfrac{{1}}{{2}}x_{{tp}}^2$,
giving
\[
  x_{{tp}} = \pm\sqrt{{2n+1}} = \pm{sp_latex(x_tp)} \approx \pm{float(x_tp):.4f}\,x_0.
\]

\end{{document}}
"""
        return doc

    def kss_bound_tex(self, bound_value: float) -> str:
        """
        Full LaTeX document for the KSS viscosity bound.

        Parameters
        ----------
        bound_value : ħ/(4π k_B) in K·s.
        """
        doc = self._preamble("KSS Viscosity Bound in QCD")
        bound_tex = _format_sci_latex(bound_value)
        doc += rf"""
\begin{{document}}
\maketitle

\section{{The Kovtun--Son--Starinets (KSS) Bound}}

Via the AdS/CFT (gauge/gravity) duality, Kovtun, Son, and Starinets (2005)
conjectured that for \emph{{any}} relativistic fluid described by a
classical gravity dual,
\[
  \frac{{\eta}}{{s}} \;\geq\; \frac{{\hbar}}{{4\pi k_B}},
\]
where $\eta$ is the shear viscosity and $s$ the entropy density.

\section{{Numerical Value}}

Using CODATA 2018 fundamental constants:
\[
  \frac{{\hbar}}{{4\pi k_B}}
  = \frac{{1.054\,571\,817 \times 10^{{-34}}~\text{{J\,s}}}}
         {{4\pi \times 1.380\,649 \times 10^{{-23}}~\text{{J/K}}}}
  = {bound_tex}~\text{{K\,s}}.
\]

\section{{Physical Significance}}

The quark-gluon plasma (QGP) created at RHIC and the LHC has been measured
with $\eta/s$ very close to---but above---this bound, making it the most
perfect liquid known in nature and the first experimental realisation of a
strongly-coupled quantum fluid near the KSS limit.

\end{{document}}
"""
        return doc

    def harmonic_oscillator_multi_tex(
        self, states: list[int], state_records: list[dict[str, Any]]
    ) -> str:
        """Full LaTeX document for QHO multiple eigenstates."""
        doc = self._preamble("Quantum Harmonic Oscillator Multi-Eigenstate Results")
        doc += r"""
\begin{document}
\maketitle

\section{Eigenstate Spectrum Summary}

\begin{table}[h!]
\centering
\begin{tabular}{cccc}
\hline
Quantum Level $n$ & Energy (nat.) & Energy (SI) & Turning Point $\pm x_{\text{tp}}$ \\
\hline
"""
        for s in state_records:
            e_si_tex = _format_sci_latex(float(s["energy"]))
            doc += rf"{s['n']} & {s['energy_nat']:.1f}\,\hbar\omega & {e_si_tex}\,\text{{J}} & \pm {s['x_tp']:.4f}\,x_0 \\" + "\n"

        doc += r"""\hline
\end{tabular}
\end{table}

\section{Analytic Wavefunctions in Dimensionless Coordinates}
The stationary states of the 1D Quantum Harmonic Oscillator in dimensionless units $\xi = x/x_0$ satisfy:
\[
  \psi_n(x) = \frac{1}{\sqrt{\sqrt{\pi}\,2^n\,n!}}\,H_n(x)\,e^{-x^2/2}.
\]
where $H_n$ is the physicists' Hermite polynomial of degree $n$, and $x_0 = \sqrt{\hbar/(m\omega)}$.

\end{document}
"""
        return doc


    def cyclotron_tex(self, data: dict[str, Any]) -> str:
        """Full LaTeX document for Cyclotron Particle Accelerator simulation."""
        b_field = data.get("B_field", 1.5)
        gap_voltage = data.get("gap_voltage", 50000.0)
        dee_radius_cm = data.get("dee_radius", 0.5) * 100.0
        freq_mhz = data.get("cyclotron_frequency_mhz", 22.87)
        final_ke = data.get("final_energy_mev", 2.194)
        final_r = data.get("final_radius_cm", 14.0)
        turns = data.get("turns", 22.9)
        flight_time_us = data.get("flight_time_us", 1.0)

        doc = self._preamble("Cyclotron Particle Accelerator Simulation Results")
        doc += rf"""
\begin{{document}}
\maketitle

\section{{Accelerator Configuration}}

\begin{{table}}[h!]
\centering
\begin{{tabular}}{{ll}}
\hline
\textbf{{Parameter}} & \textbf{{Value}} \\
\hline
Magnetic Field $B$ & {b_field:.2f}~\mathrm{{T}} \\
RF Gap Voltage $V_{{\mathrm{{gap}}}}$ & {gap_voltage/1000:.1f}~\mathrm{{kV}} \\
Dee Radius $R_{{\mathrm{{dee}}}}$ & {dee_radius_cm:.1f}~\mathrm{{cm}} \\
Cyclotron Resonance Frequency $f_c$ & {freq_mhz:.2f}~\mathrm{{MHz}} \\
\hline
\end{{tabular}}
\end{{table}}

\section{{Governing Dynamics}}
The motion of the accelerated ion is governed by the Lorentz force:
\[
  \mathbf{{F}} = q\left(\mathbf{{E}}(\mathbf{{x}}, t) + \mathbf{{v}} \times \mathbf{{B}}\right).
\]
In the constant magnetic field $\mathbf{{B}} = B\,\hat{{\mathbf{{z}}}}$, the orbital resonance frequency is:
\[
  \omega_c = \frac{{qB}}{{m}}, \quad f_c = \frac{{\omega_c}}{{2\pi}}.
\]

\section{{Simulation Results}}

\begin{{itemize}}
  \item \textbf{{Final Kinetic Energy:}} ${final_ke:.3f}~\mathrm{{MeV}}$
  \item \textbf{{Exit Orbital Radius:}} ${final_r:.1f}~\mathrm{{cm}}$
  \item \textbf{{Total Turns Completed:}} $\sim {turns:.1f}$
  \item \textbf{{Total Flight Time:}} ${flight_time_us:.2f}~\mu\mathrm{{s}}$
\end{{itemize}}

\end{{document}}
"""
        return doc


    # ── High-level API ────────────────────────────────────────────────────────

    def generate_and_save(self, topic: str, **kwargs) -> Path | None:
        """
        Generate and save a LaTeX document for the given physics topic.

        Parameters
        ----------
        topic    : 'harmonic_oscillator', 'harmonic_oscillator_multi', 'cyclotron', or 'kss_bound'.
        **kwargs : Topic-specific keyword arguments.

        Returns
        -------
        Path to the saved .tex file, or None if the topic is unknown.
        """
        if topic == "harmonic_oscillator":
            n      = int(kwargs.get("n", 0))
            energy = float(kwargs.get("energy", 0.0))
            return self._save_tex(self.harmonic_oscillator_tex(n, energy), f"qho_n{n}")

        if topic == "harmonic_oscillator_multi":
            states = kwargs.get("states", [0, 1, 2, 3])
            state_records = kwargs.get("state_records", [])
            states_tag = "_".join(str(s) for s in states)
            return self._save_tex(
                self.harmonic_oscillator_multi_tex(states, state_records),
                f"qho_multi_eigenstates_{states_tag}",
            )

        if topic == "cyclotron":
            return self._save_tex(self.cyclotron_tex(kwargs), "cyclotron_simulation")

        if topic == "kss_bound":
            bound = float(kwargs.get("bound_value", 0.0))
            return self._save_tex(self.kss_bound_tex(bound), "kss_bound")

        logger.warning("Unknown LaTeX topic: %r", topic)
        return None

