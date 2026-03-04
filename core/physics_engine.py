"""
Physics Engine Module
Implements core physics calculations: Quantum Harmonic Oscillator and QCD concepts.
"""

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
from scipy import constants
from scipy.special import hermite, factorial
from pathlib import Path
import logging
from typing import Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuantumHarmonicOscillator:
    """
    Represents a 1D quantum harmonic oscillator.

    Attributes:
        mass (float): Particle mass (default 1.0 in natural units).
        omega (float): Angular frequency (default 1.0).
        hbar (float): Reduced Planck constant (uses scipy.constants).
    """

    def __init__(self, mass: float = 1.0, omega: float = 1.0):
        self.mass = mass
        self.omega = omega
        self.hbar = constants.hbar  # J·s

    def energy(self, n: int) -> float:
        """
        Energy eigenvalue for level n.

        Args:
            n: Quantum number (non-negative integer).

        Returns:
            Energy in Joules.

        Raises:
            ValueError: If n is negative.
        """
        if n < 0:
            raise ValueError("Quantum number n must be non-negative.")
        return self.hbar * self.omega * (n + 0.5)

    def _alpha(self) -> float:
        """Return the inverse length scale alpha = sqrt(m*omega/hbar)."""
        return np.sqrt(self.mass * self.omega / self.hbar)

    def wavefunction(self, n: int, x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """
        Compute the wavefunction psi_n(x) for the harmonic oscillator.

        Uses the Hermite polynomial representation:
        psi_n(x) = (alpha / (sqrt(pi) * 2^n * n!))^{1/2} * H_n(xi) * exp(-xi^2/2)
        where xi = alpha * x.

        Args:
            n: Quantum number.
            x: Array of positions (in meters).

        Returns:
            Array of wavefunction values.

        Raises:
            ValueError: If n is negative.
        """
        if n < 0:
            raise ValueError("Quantum number n must be non-negative.")

        alpha = self._alpha()
        xi = alpha * x
        # Prefactor: (alpha / (sqrt(pi) * 2^n * n!))^{1/2}
        prefactor = np.sqrt(alpha / (np.sqrt(np.pi) * (2.0**n) * factorial(n)))
        herm = hermite(n)(xi)  # Evaluate Hermite polynomial
        psi = prefactor * herm * np.exp(-0.5 * xi**2)
        return psi

    def probability_density(self, n: int, x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """
        Compute probability density |psi_n(x)|^2.

        Args:
            n: Quantum number.
            x: Array of positions.

        Returns:
            Array of probability densities.
        """
        psi = self.wavefunction(n, x)
        return np.abs(psi) ** 2

    def plot_wavefunction(
        self,
        n: int,
        x_range: Tuple[float, float] = (-5.0, 5.0),
        num_points: int = 1000,
        save_path: Optional[Union[str, Path]] = None,
    ) -> plt.Figure:
        """
        Plot the wavefunction and probability density for level n.

        Args:
            n: Quantum number.
            x_range: (min, max) position in meters.
            num_points: Number of points for x grid.
            save_path: If provided, save the figure to this path.

        Returns:
            Matplotlib Figure object.
        """
        x = np.linspace(x_range[0], x_range[1], num_points)
        psi = self.wavefunction(n, x)
        prob = self.probability_density(n, x)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        fig.suptitle(f"Quantum Harmonic Oscillator (n={n})")

        ax1.plot(x, psi, "b-", label=r"$\psi_n(x)$")
        ax1.set_ylabel(r"$\psi_n(x)$")
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        ax2.plot(x, prob, "r-", label=r"$|\psi_n(x)|^2$")
        ax2.set_xlabel("Position x (m)")
        ax2.set_ylabel("Probability density")
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()

        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved wavefunction plot to {save_path}")

        return fig


class QCDConcepts:
    """
    Implements selected non-perturbative QCD concepts, including the KSS bound.
    """

    def __init__(self):
        self.hbar = constants.hbar
        self.k_B = constants.k  # Boltzmann constant

    def kss_bound_value(self) -> float:
        """
        Compute the Kovtun-Son-Starinets (KSS) bound:
            eta / s >= hbar / (4 * pi * k_B)

        Returns:
            Lower bound value for eta/s in natural units (J·s / (J/K) = K·s).
        """
        return self.hbar / (4.0 * np.pi * self.k_B)

    def plot_kss_bound(
        self,
        temperature_range: Tuple[float, float] = (1e-6, 1e-4),  # Kelvin
        hypothetical_data: Optional[Tuple[npt.NDArray, npt.NDArray]] = None,
        save_path: Optional[Union[str, Path]] = None,
    ) -> plt.Figure:
        """
        Plot the KSS bound as a horizontal line, optionally with hypothetical data.

        Args:
            temperature_range: (T_min, T_max) for the plot.
            hypothetical_data: Optional (T_array, eta_over_s_array) to overlay.
            save_path: If provided, save the figure.

        Returns:
            Matplotlib Figure.
        """
        T_min, T_max = temperature_range
        T = np.linspace(T_min, T_max, 100)
        bound = self.kss_bound_value() * np.ones_like(T)  # constant bound

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.semilogy(T, bound, "k--", label=r"KSS bound $\frac{\hbar}{4\pi k_B}$")

        if hypothetical_data is not None:
            T_data, eta_s_data = hypothetical_data
            ax.semilogy(T_data, eta_s_data, "ro", markersize=4, label="Hypothetical QGP data")

        ax.set_xlabel("Temperature T (K)")
        ax.set_ylabel(r"Shear viscosity / entropy density $\eta/s$ (K·s)")
        ax.set_title("KSS Bound for Quark-Gluon Plasma")
        ax.grid(True, alpha=0.3, which="both")
        ax.legend()

        # Shade forbidden region
        y_min, y_max = ax.get_ylim()
        ax.fill_between(T, y_min, bound, where=(bound > y_min), color="red", alpha=0.1, label="Forbidden")
        ax.set_ylim(bottom=y_min)

        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved KSS bound plot to {save_path}")

        return fig

    def generate_hypothetical_qgp_data(
        self, T_min: float = 1e-6, T_max: float = 1e-4, num_points: int = 20, noise: float = 0.1
    ) -> Tuple[npt.NDArray, npt.NDArray]:
        """
        Generate hypothetical QGP data for demonstration purposes.

        Args:
            T_min, T_max: Temperature range (K).
            num_points: Number of data points.
            noise: Relative noise amplitude.

        Returns:
            (T_array, eta_s_array)
        """
        T = np.linspace(T_min, T_max, num_points)
        bound = self.kss_bound_value()
        # Create data that mostly satisfies bound, with some points near/above it
        eta_s = bound * (1.5 + 0.5 * np.random.randn(num_points))
        eta_s = np.maximum(eta_s, bound * 0.8)  # some slightly below bound to show violation
        return T, eta_s


class PhysicsEngine:
    """
    High-level interface to all physics modules.
    """

    def __init__(self, export_dir: Path):
        self.export_dir = export_dir
        self.qho = QuantumHarmonicOscillator()
        self.qcd = QCDConcepts()

    def harmonic_oscillator_wavefunction(
        self, n: int, x_range: Tuple[float, float] = (-5.0, 5.0), save_plot: bool = True
    ) -> dict:
        """
        Compute and optionally plot harmonic oscillator wavefunction.

        Args:
            n: Quantum number.
            x_range: Position range.
            save_plot: If True, save plot to export directory.

        Returns:
            Dictionary with keys: 'n', 'energy', 'plot_path' (if saved), 'x', 'psi', 'prob'.
        """
        x = np.linspace(x_range[0], x_range[1], 1000)
        psi = self.qho.wavefunction(n, x)
        prob = self.qho.probability_density(n, x)
        energy = self.qho.energy(n)

        result = {
            "n": n,
            "energy": energy,
            "x": x.tolist(),
            "psi": psi.tolist(),
            "prob": prob.tolist(),
            "plot_path": None,
        }

        if save_plot:
            plot_filename = self.export_dir / f"qho_n{n}_wavefunction.png"
            self.qho.plot_wavefunction(n, x_range=x_range, save_path=plot_filename)
            result["plot_path"] = str(plot_filename)

        return result

    def kss_bound(self, generate_sample_data: bool = True, save_plot: bool = True) -> dict:
        """
        Compute KSS bound and optionally generate a plot.

        Args:
            generate_sample_data: Whether to overlay hypothetical QGP data.
            save_plot: If True, save plot.

        Returns:
            Dictionary with bound value and plot path.
        """
        bound_value = self.qcd.kss_bound_value()
        result = {"bound_value": bound_value, "plot_path": None}

        if save_plot:
            data = None
            if generate_sample_data:
                T, eta_s = self.qcd.generate_hypothetical_qgp_data()
                data = (T, eta_s)

            plot_filename = self.export_dir / "kss_bound.png"
            self.qcd.plot_kss_bound(hypothetical_data=data, save_path=plot_filename)
            result["plot_path"] = str(plot_filename)

        return result