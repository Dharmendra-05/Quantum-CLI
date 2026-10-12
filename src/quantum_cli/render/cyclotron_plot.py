r"""
Cyclotron Trajectory & Energy Gain Visualizer
=============================================
Renders high-fidelity dual-panel figures displaying:
  1. The 2D spiral particle trajectory across the Dees colored by kinetic energy.
  2. Kinetic energy accumulation as a function of orbital radius.

Dark-theme publication aesthetic adapted for Quantum-CLI.
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
_CYAN = "#58a6ff"
_GREEN = "#3fb950"
_ORANGE = "#d29922"
_RED = "#f85149"


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


def plot_cyclotron_trajectory(
    sim_data: dict[str, Any],
    save_path: str | Path,
    dpi: int = 150,
) -> Path:
    r"""
    Generates a dual-panel visualization of the cyclotron simulation:
      - Left panel : 2D trajectory spiral (x vs y in cm) colored by kinetic energy.
      - Right panel: Kinetic energy (MeV) vs orbital radius (cm).

    Parameters
    ----------
    sim_data  : Output dictionary from CyclotronSimulator.simulate().
    save_path : Destination filepath for the rendered PNG image.
    dpi       : Output figure resolution in dots per inch (default 150).

    Returns
    -------
    Path to the saved PNG file.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import Normalize

    trajectory = sim_data["trajectory"]
    energy_profile = sim_data["energy_mev"]
    b_field = sim_data["B_field"]
    gap_voltage = sim_data["gap_voltage"]
    dee_radius_cm = sim_data["dee_radius"] * 100.0
    gap_width_cm = sim_data["gap_width"] * 100.0
    freq_mhz = sim_data["cyclotron_frequency_mhz"]
    final_ke = sim_data["final_energy_mev"]
    final_r = sim_data["final_radius_cm"]
    turns = sim_data["turns"]

    # Convert coordinates to cm
    x_cm = trajectory[0] * 100.0
    y_cm = trajectory[1] * 100.0

    fig, (ax1, ax2) = plt.subplots(
        1, 2,
        figsize=(14, 7),
        facecolor=_BG,
        gridspec_kw={"wspace": 0.22},
    )

    # ── Left Panel: Main Trajectory with Energy Colormap ───────────────────────
    _style_axes(ax1)

    # Draw Dee boundary circle
    theta = np.linspace(0, 2 * np.pi, 300)
    ax1.plot(
        dee_radius_cm * np.cos(theta),
        dee_radius_cm * np.sin(theta),
        color="#30363d",
        linestyle="--",
        linewidth=1.2,
        label=rf"Dee Radius ($R = {dee_radius_cm:.1f}\,$cm)",
        zorder=1,
    )

    # Shaded accelerating gap strip
    ax1.axhspan(-gap_width_cm / 2, gap_width_cm / 2, color="#21262d", alpha=0.6, zorder=0)

    # Color segments by kinetic energy
    norm = Normalize(vmin=energy_profile.min(), vmax=energy_profile.max())
    cmap = plt.cm.plasma

    # Downsample points for line drawing if trajectory is very large
    step = max(1, len(x_cm) // 1500)
    for i in range(0, len(x_cm) - step, step):
        col = cmap(norm(energy_profile[i]))
        ax1.plot(x_cm[i:i+step+1], y_cm[i:i+step+1], color=col, linewidth=1.6, zorder=2)

    # Starting and exit markers
    ax1.scatter([x_cm[0]], [y_cm[0]], color=_GREEN, s=70, zorder=4, label="Injection Point")
    ax1.scatter([x_cm[-1]], [y_cm[-1]], color=_RED, s=120, marker="*", zorder=4, label="Exit Beam")

    ax1.set_xlabel(r"Position  $x$  (cm)", fontsize=11)
    ax1.set_ylabel(r"Position  $y$  (cm)", fontsize=11)
    ax1.set_title("Cyclotron Spiral Trajectory", fontsize=13, fontweight="bold", pad=10)
    ax1.set_aspect("equal")

    # Info badge
    info_text = (
        rf"$B = {b_field:.2f}\,\mathrm{{T}}$" + "\n"
        rf"$V_{{\mathrm{{gap}}}} = {gap_voltage/1000:.1f}\,\mathrm{{kV}}$" + "\n"
        rf"$f_c = {freq_mhz:.2f}\,\mathrm{{MHz}}$"
    )
    ax1.text(
        0.04, 0.96, info_text,
        transform=ax1.transAxes,
        fontsize=9.5,
        color=_TEXT,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.4", fc=_AX_BG, ec=_BORDER, alpha=0.9),
    )

    ax1.legend(
        loc="lower left",
        facecolor=_AX_BG,
        edgecolor=_BORDER,
        labelcolor=_TEXT,
        fontsize=9,
    )

    # Colorbar
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax1, fraction=0.046, pad=0.04)
    cbar.set_label("Kinetic Energy (MeV)", color=_TEXT_DIM, fontsize=10)
    cbar.ax.tick_params(colors=_TEXT_DIM, labelsize=8.5)
    cbar.outline.set_edgecolor(_BORDER)

    # ── Right Panel: Energy Gain vs Orbital Radius ────────────────────────────
    _style_axes(ax2)

    radius_cm = np.sqrt(x_cm**2 + y_cm**2)

    ax2.plot(radius_cm, energy_profile, color=_CYAN, linewidth=2.0, label="Proton Energy $E_k(r)$")
    ax2.fill_between(radius_cm, energy_profile, color=_CYAN, alpha=0.18)

    ax2.set_xlabel(r"Orbital Radius  $r = \sqrt{x^2 + y^2}$  (cm)", fontsize=11)
    ax2.set_ylabel(r"Kinetic Energy  $E_k$  (MeV)", fontsize=11)
    ax2.set_title("Energy Gain vs Orbital Radius", fontsize=13, fontweight="bold", pad=10)

    # Summary box
    summary_text = (
        f"Final Energy: {final_ke:.3f} MeV\n"
        f"Exit Radius:  {final_r:.1f} cm\n"
        f"Revolutions:  ~{turns:.1f} turns"
    )
    ax2.text(
        0.05, 0.95, summary_text,
        transform=ax2.transAxes,
        fontsize=9.5,
        color=_ORANGE,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.4", fc=_AX_BG, ec=_BORDER, alpha=0.9),
    )

    ax2.legend(
        loc="lower right",
        facecolor=_AX_BG,
        edgecolor=_BORDER,
        labelcolor=_TEXT,
        fontsize=9.5,
    )

    # ── Global Title ──────────────────────────────────────────────────────────
    fig.suptitle(
        r"Cyclotron Particle Accelerator — Lorentz Force Trajectory & Resonant RF Acceleration",
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
