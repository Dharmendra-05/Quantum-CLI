"""
LaTeX Generator Module
Produces .tex files for physics results using sympy for symbolic expressions.
"""

import sympy as sp
from sympy import latex
import numpy as np
from pathlib import Path
import logging
from typing import Union, Optional

logger = logging.getLogger(__name__)


class LaTeXGenerator:
    """
    Generates LaTeX code for various physics outputs.
    """

    def __init__(self, export_dir: Path):
        self.export_dir = export_dir
        # Ensure export directory exists
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def _save_tex(self, content: str, filename: str) -> Path:
        """
        Save content to a .tex file in the export directory.

        Args:
            content: LaTeX string.
            filename: Name of the file (without .tex extension).

        Returns:
            Path to the saved file.
        """
        filepath = self.export_dir / f"{filename}.tex"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Saved LaTeX to {filepath}")
        return filepath

    def harmonic_oscillator_tex(self, n: int, energy: float) -> str:
        """
        Generate LaTeX document for harmonic oscillator results.

        Args:
            n: Quantum number.
            energy: Energy value in Joules.

        Returns:
            Full LaTeX document as a string.
        """
        # Symbolic representation
        x = sp.Symbol("x", real=True)
        alpha = sp.Symbol(r"\alpha", positive=True)
        # Hermite polynomial
        H_n = sp.hermite(n, x)
        # Wavefunction symbolic form (without normalization)
        psi_sym = H_n * sp.exp(-x**2 / 2)

        # LaTeX
        doc = rf"""
\documentclass{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{geometry}}
\geometry{{a4paper, margin=1in}}

\title{{Quantum Harmonic Oscillator Results}}
\author{{Quantum-CLI Toolkit}}
\date{{\today}}

\begin{{document}}
\maketitle

\section{{Energy Level n = {n}}}
The energy eigenvalue is:
\[
E_{{{n}}} = \hbar \omega \left(n + \frac{{1}}{{2}}\right) = {energy:.3e}~\text{{J}}.
\]

\section{{Wavefunction}}
The wavefunction \(\psi_{{{n}}}(x)\) is given by:
\[
\psi_{{{n}}}(x) = \frac{{\alpha^{{1/2}}}}{{\sqrt{{\sqrt{{\pi}} 2^{{n}} n!}}}}
H_{{{n}}}(\alpha x) e^{{-\alpha^2 x^2/2}},
\]
where \(\alpha = \sqrt{{m\omega/\hbar}}\).

Using symbolic representation:
\[
\psi_{{{n}}}(x) \propto {latex(psi_sym)}.
\]

\end{{document}}
"""
        return doc

    def kss_bound_tex(self, bound_value: float) -> str:
        """
        Generate LaTeX document for KSS bound.

        Args:
            bound_value: Numerical value of the bound (η/s).

        Returns:
            Full LaTeX document as a string.
        """
        doc = rf"""
\documentclass{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{geometry}}
\geometry{{a4paper, margin=1in}}

\title{{KSS Bound in QCD}}
\author{{Quantum-CLI Toolkit}}
\date{{\today}}

\begin{{document}}
\maketitle

\section{{The Kovtun–Son–Starinets Bound}}
For any fluid described by Einstein gravity via the gauge/gravity duality,
the ratio of shear viscosity \(\eta\) to entropy density \(s\) satisfies
\[
\frac{{\eta}}{{s}} \ge \frac{{\hbar}}{{4\pi k_B}}.
\]

\section{{Numerical Value}}
Using fundamental constants:
\[
\frac{{\hbar}}{{4\pi k_B}} = {bound_value:.3e}~\text{{K·s}}.
\]

\end{{document}}
"""
        return doc

    def generate_and_save(self, topic: str, **kwargs) -> Optional[Path]:
        """
        High-level method to generate and save LaTeX for a given topic.

        Args:
            topic: One of 'harmonic_oscillator', 'kss_bound'.
            **kwargs: Arguments specific to the topic.

        Returns:
            Path to the saved .tex file, or None if topic unknown.
        """
        if topic == "harmonic_oscillator":
            n = kwargs.get("n", 0)
            energy = kwargs.get("energy", 0.0)
            content = self.harmonic_oscillator_tex(n, energy)
            filename = f"qho_n{n}"
            return self._save_tex(content, filename)
        elif topic == "kss_bound":
            bound = kwargs.get("bound_value", 0.0)
            content = self.kss_bound_tex(bound)
            filename = "kss_bound"
            return self._save_tex(content, filename)
        else:
            logger.warning(f"Unknown LaTeX topic: {topic}")
            return None