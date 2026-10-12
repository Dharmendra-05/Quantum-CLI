import pytest
from quantum_cli.core.physics_engine import QuantumHarmonicOscillator, QCDConcepts

def test_qho_energy_level_natural_and_si():
    qho = QuantumHarmonicOscillator()
    # Natural units (hbar = m = omega = 1): E_3 = 3 + 0.5 = 3.5
    assert qho.energy_natural(3) == 3.5
    # SI units (E = 3.5 * hbar ≈ 3.691e-34 J)
    e_si = qho.energy(3)
    assert pytest.approx(3.691e-34, rel=1e-3) == e_si

def test_qcd_kss_bound_value():
    qcd = QCDConcepts()
    kss = qcd.kss_bound_value()
    # KSS Bound: hbar / (4 * pi * k_B) ≈ 6.0794e-13 K·s
    assert pytest.approx(6.0794e-13, rel=1e-4) == kss
