r"""
QHO Multi-Eigenstate Renderer
=============================
Generates publication-quality dual-panel visualizations of Quantum Harmonic
Oscillator eigenstates and probability densities embedded within the parabolic
potential well V(x) = 1/2 m \omega^2 x^2.

Ported from QHO-Eigenstate-Visualizer and adapted for the Quantum-CLI
dark-themed rendering pipeline.
"""

from pathlib import Path
from typing import Any

# Dark-theme color palette (GitHub-dark aesthetic)
_BG = "#0d1117"
_AX_BG = "#161b22"
_GRID = "#21262d"
_BORDER = "#30363d"
_TEXT = "#c9d1d9"
_TEXT_DIM = "#8b949e"
_POTENTIAL = "#484f58"


def _style_axes(ax: Any) -> None:
    """Apply dark-theme palette styling to a Matplotlib Axes object."""
    ax.set_facecolor(_AX_BG)
    ax.tick_params(colors=_TEXT_DIM, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(_BORDER)
    ax.xaxis.label.set_color(_TEXT_DIM)
    ax.yaxis.label.set_color(_TEXT_DIM)
    ax.title.set_color(_TEXT)
    ax.grid(True, color=_GRID, linewidth=0.6, alpha=0.85)


def plot_multi_eigenstates(
    data: dict[str, Any],
    save_path: str | Path,
    amplitude_scale: float = 0.45,
    cmap_name: str = "plasma",
    dpi: int = 150,
) -> Path:
    r"""
    Renders a dual-panel figure for multiple QHO eigenstates:
      - Left panel : Wavefunctions \psi_n(x) offset vertically by energy E_n.
      - Right panel: Probability densities |\psi_n(x)|^2 offset vertically by E_n.

    Both panels display the underlying parabolic potential V(x) and annotate
    classical turning points to visualize quantum tunneling / barrier penetration.

    Parameters
    ----------
    data            : Output dict from QuantumHarmonicOscillator.multi_eigenstates().
                      Must contain 'x', 'states', and 'x_range'.
    save_path       : Destination filepath for the rendered PNG image.
    amplitude_scale : Vertical scaling factor for wavefunction / density curves.
    cmap_name       : Matplotlib colormap used to distinguish energy levels.
    dpi             : Rendering resolution in dots per inch (default 150).

    Returns
    -------
    Path to the saved PNG file.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import numpy as np
    from matplotlib.lines import Line2D

    x = data["x"]
    states = data["states"]
    x_range = data["x_range"]
    n_states = len(states)

    if n_states == 0:
        raise ValueError("Cannot plot empty eigenstates data.")

    # Colormap sampling
    cmap = plt.get_cmap(cmap_name)
    if n_states == 1:
        colors = [cmap(0.6)]
    else:
        colors = [cmap(v) for v in np.linspace(0.2, 0.85, n_states)]

    # Potential energy curve V(x) = 1/2 m \omega^2 x^2 (in natural units m=omega=1)
    v_potential = 0.5 * (x ** 2)

    max_energy = max(s["energy_nat"] for s in states)
    y_min = -0.4
    y_max = max_energy + 1.4

    fig, axes = plt.subplots(
        1, 2,
        figsize=(14, 7),
        sharey=True,
        facecolor=_BG,
        gridspec_kw={"wspace": 0.06},
    )
    ax_psi, ax_prob = axes

    for ax in axes:
        _style_axes(ax)
        # Parabolic potential
        ax.plot(
            x, v_potential,
            color=_POTENTIAL, lw=1.6, ls="--", zorder=1,
            label=r"$V(x) = \frac{1}{2}m\omega^2 x^2$",
        )
        ax.set_xlim(x_range[0], x_range[1])
        ax.set_ylim(y_min, y_max)
        ax.yaxis.set_major_locator(ticker.MultipleLocator(1.0))
        ax.set_xlabel(r"Position  $x / x_0$  (dimensionless)", fontsize=11)

    # ── Left Panel: Wavefunctions \psi_n(x) ───────────────────────────────────
    for idx, s in enumerate(states):
        n = s["n"]
        e_nat = s["energy_nat"]
        psi = s["psi"]
        x_tp = s["x_tp"]
        col = colors[idx]

        y_curve = e_nat + amplitude_scale * psi

        ax_psi.plot(x, y_curve, color=col, lw=2.0, zorder=3)
        ax_psi.fill_between(
            x, e_nat, y_curve, where=(y_curve >= e_nat),
            color=col, alpha=0.35, zorder=2,
        )
        ax_psi.fill_between(
            x, e_nat, y_curve, where=(y_curve < e_nat),
            color=col, alpha=0.15, zorder=2,
        )

        # Dotted line at the energy level between turning points
        ax_psi.hlines(e_nat, -x_tp, x_tp, color=col, lw=1.0, ls=":", alpha=0.8, zorder=2)

        # Right-margin energy annotation
        ax_psi.text(
            x_range[1] * 0.95, e_nat,
            rf"$E_{{{n}}} = {e_nat:.1f}\,\hbar\omega$",
            va="center", ha="right", fontsize=9.5, color=col,
            bbox=dict(boxstyle="round,pad=0.2", fc=_AX_BG, ec=_BORDER, alpha=0.85),
        )

    ax_psi.set_title(r"Wavefunctions  $\psi_n(x)$", fontsize=13, fontweight="bold", pad=10)
    ax_psi.set_ylabel(r"Energy  $E\,/\,\hbar\omega$", fontsize=11)

    legend_handles_psi = [
        Line2D([0], [0], color=colors[i], lw=2.2, label=rf"$n = {states[i]['n']}$")
        for i in range(n_states)
    ]
    ax_psi.legend(
        handles=legend_handles_psi,
        loc="upper left",
        facecolor=_AX_BG,
        edgecolor=_BORDER,
        labelcolor=_TEXT,
        fontsize=9.5,
    )

    # ── Right Panel: Probability Densities |\psi_n(x)|^2 ──────────────────────
    for idx, s in enumerate(states):
        e_nat = s["energy_nat"]
        prob = s["prob"]
        x_tp = s["x_tp"]
        col = colors[idx]

        y_curve = e_nat + amplitude_scale * prob

        ax_prob.plot(x, y_curve, color=col, lw=2.0, zorder=3)
        ax_prob.fill_between(x, e_nat, y_curve, color=col, alpha=0.35, zorder=2)

        # Dotted line at energy level between turning points
        ax_prob.hlines(e_nat, -x_tp, x_tp, color=col, lw=1.0, ls=":", alpha=0.8, zorder=2)

        # Vertical dashed turning point markers
        for sign in (-1, 1):
            ax_prob.axvline(
                sign * x_tp, color=col, lw=0.8, ls="--", alpha=0.55, zorder=1,
            )

    ax_prob.set_title(
        r"Probability Densities  $|\psi_n(x)|^2$", fontsize=13, fontweight="bold", pad=10
    )

    legend_handle_v = Line2D(
        [0], [0], color=_POTENTIAL, lw=1.6, ls="--", label=r"$V(x) = \frac{1}{2}m\omega^2 x^2$"
    )
    ax_prob.legend(
        handles=[legend_handle_v],
        loc="upper left",
        facecolor=_AX_BG,
        edgecolor=_BORDER,
        labelcolor=_TEXT,
        fontsize=9.5,
    )

    # Global Title
    fig.suptitle(
        r"Quantum Harmonic Oscillator — Multi-Eigenstate Potential Well "
        r"($m=1,\;\omega=1,\;\hbar=1$)",
        color=_TEXT,
        fontsize=14,
        fontweight="bold",
        y=0.98,
    )

    out_file = Path(save_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_file, dpi=dpi, bbox_inches="tight", facecolor=_BG)
    plt.close(fig)

    return out_file
