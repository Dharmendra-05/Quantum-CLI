"""
Cyclotron Particle Accelerator Simulation Engine
=================================================
High-fidelity pure physics solver for charged particle motion in a cyclotron.
Simulates proton trajectories under the Lorentz force with resonant RF electric
acceleration across the D-shaped electrode (Dee) gap.

Physics Principles:
    Lorentz Force:
        F = q(E + v × B)
    Cyclotron Resonance Frequency:
        ω_c = qB / m  (rad/s),   f_c = ω_c / (2π)  (Hz)
    Kinetic Energy:
        E_k = 1/2 m v² (Joules) = (1/2 m v²) / (1.602176634 × 10⁻¹³ J/MeV)

This module belongs strictly to the `core/` layer and contains zero GUI,
zero Matplotlib, zero Rich, and zero file I/O dependencies.
"""

from dataclasses import dataclass
from typing import Any

import numpy as np
import scipy.integrate as integrate


@dataclass(frozen=True)
class PhysicalConstants:
    """Fundamental physical constants in SI units (CODATA 2018)."""
    proton_charge: float = 1.602176634e-19   # Coulombs (C)
    proton_mass: float = 1.67262192369e-27   # Kilograms (kg)
    speed_of_light: float = 299792458.0      # Metres per second (m/s)
    mev_to_joules: float = 1.602176634e-13   # Joules per MeV


class CyclotronSimulator:
    """
    Simulates proton dynamics in a classic Lawrence cyclotron.

    The proton starts near the center of the accelerating gap and spirals
    outward under a perpendicular uniform magnetic field (B_z) while receiving
    periodic energy boosts each time it traverses the alternating RF electric gap.

    Attributes
    ----------
    B_field : float
        Uniform magnetic field strength in Tesla (pointing in +z direction).
    gap_voltage : float
        Peak RF potential difference across the Dee gap in Volts.
    dee_radius : float
        Maximum radius of the D-shaped electrodes in metres.
    gap_width : float
        Physical width of the accelerating gap in metres.
    constants : PhysicalConstants
        Physical constants used in the calculation.
    """

    def __init__(
        self,
        B_field: float = 1.5,
        gap_voltage: float = 50000.0,
        dee_radius: float = 0.5,
        gap_width: float = 0.01,
        constants: PhysicalConstants | None = None,
    ) -> None:
        if B_field <= 0:
            raise ValueError(f"Magnetic field B_field must be positive, got {B_field}")
        if gap_voltage <= 0:
            raise ValueError(f"Gap voltage must be positive, got {gap_voltage}")
        if dee_radius <= 0:
            raise ValueError(f"Dee radius must be positive, got {dee_radius}")
        if gap_width <= 0:
            raise ValueError(f"Gap width must be positive, got {gap_width}")

        self.B_field = float(B_field)
        self.gap_voltage = float(gap_voltage)
        self.dee_radius = float(dee_radius)
        self.gap_width = float(gap_width)
        self.constants = constants or PhysicalConstants()

        self.q = self.constants.proton_charge
        self.m = self.constants.proton_mass

        # Derived resonant frequencies
        self.omega_c: float = self.q * self.B_field / self.m
        self.freq_c_hz: float = self.omega_c / (2.0 * np.pi)
        self.freq_c_mhz: float = self.freq_c_hz / 1e6

    # ── Equations of Motion ───────────────────────────────────────────────────

    def _get_electric_field(self, y: float, t: float) -> np.ndarray:
        """Calculate localized alternating RF electric field in the Dee gap."""
        E_vec = np.zeros(3, dtype=np.float64)
        if abs(y) < (self.gap_width / 2.0):
            field_magnitude = self.gap_voltage / self.gap_width
            phase = np.cos(self.omega_c * t)
            E_vec[1] = field_magnitude * phase
        return E_vec

    def _lorentz_force(self, t: float, state: np.ndarray) -> np.ndarray:
        """Compute state derivative [dx/dt, dy/dt, dz/dt, dvx/dt, dvy/dt, dvz/dt]."""
        _, y, _, vx, vy, vz = state

        # Uniform magnetic field along +z
        B_vec = np.array([0.0, 0.0, self.B_field], dtype=np.float64)
        v_vec = np.array([vx, vy, vz], dtype=np.float64)
        v_cross_B = np.cross(v_vec, B_vec)

        # Electric field in gap
        E_vec = self._get_electric_field(y, t)

        # Acceleration a = (q/m)(E + v × B)
        a_vec = (self.q / self.m) * (E_vec + v_cross_B)

        return np.array([vx, vy, vz, a_vec[0], a_vec[1], a_vec[2]], dtype=np.float64)

    def get_kinetic_energy_mev(self, velocity: np.ndarray) -> float:
        """Compute kinetic energy in MeV from a 3D velocity vector."""
        v_mag = float(np.linalg.norm(velocity))
        ke_joules = 0.5 * self.m * (v_mag ** 2)
        return float(ke_joules / self.constants.mev_to_joules)

    # ── Simulation Runner ─────────────────────────────────────────────────────

    def simulate(
        self,
        t_span: tuple[float, float] = (0.0, 1.0e-6),
        initial_velocity: float = 1.0e4,
        num_points: int = 4000,
        method: str = "DOP853",
    ) -> dict[str, Any]:
        """
        Integrate the equations of motion until particle reaches the Dee radius.

        Parameters
        ----------
        t_span : tuple[float, float]
            Integration interval (t_start, t_end) in seconds.
        initial_velocity : float
            Initial speed in m/s at the injection center.
        num_points : int
            Number of points for output trajectory interpolation.
        method : str
            ODE integration method supported by scipy.integrate.solve_ivp (default 'DOP853').

        Returns
        -------
        dict with simulation observables and trajectory arrays.
        """
        state_0 = np.array([0.0, 0.0, 0.0, initial_velocity, 0.0, 0.0], dtype=np.float64)

        # Event: terminate integration when orbital radius exceeds Dee radius
        def radius_limit(t: float, state: np.ndarray) -> float:
            x, y = state[0], state[1]
            return float(self.dee_radius - np.sqrt(x**2 + y**2))

        radius_limit.terminal = True
        radius_limit.direction = -1

        sol = integrate.solve_ivp(
            self._lorentz_force,
            t_span,
            state_0,
            method=method,
            dense_output=True,
            events=radius_limit,
            max_step=1.0e-9,
            rtol=1.0e-8,
            atol=1.0e-11,
        )

        t_eval = np.linspace(sol.t[0], sol.t[-1], num_points)
        sol_dense = sol.sol(t_eval)

        positions = sol_dense[:3]      # x, y, z in metres
        velocities = sol_dense[3:]     # vx, vy, vz in m/s

        energies_mev = np.array(
            [self.get_kinetic_energy_mev(velocities[:, i]) for i in range(num_points)],
            dtype=np.float64,
        )

        final_x, final_y = positions[0, -1], positions[1, -1]
        final_radius_m = float(np.sqrt(final_x**2 + final_y**2))
        final_radius_cm = final_radius_m * 100.0

        # Estimate turn count from total flight time and cyclotron period
        period = 1.0 / self.freq_c_hz
        flight_time_s = float(sol.t[-1])
        turns = flight_time_s / period

        return {
            "t": t_eval,
            "trajectory": positions,
            "velocities": velocities,
            "energy_mev": energies_mev,
            "B_field": self.B_field,
            "gap_voltage": self.gap_voltage,
            "dee_radius": self.dee_radius,
            "gap_width": self.gap_width,
            "cyclotron_frequency_mhz": self.freq_c_mhz,
            "omega_c": self.omega_c,
            "initial_energy_mev": float(energies_mev[0]),
            "final_energy_mev": float(energies_mev[-1]),
            "final_radius_cm": final_radius_cm,
            "flight_time_us": flight_time_s * 1e6,
            "turns": turns,
            "solver_status": int(sol.status),
        }
