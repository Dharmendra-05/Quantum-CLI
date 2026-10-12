import pytest

from quantum_cli.core.physics_engine import QCDConcepts, QuantumHarmonicOscillator


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

def test_qho_multi_eigenstates():
    qho = QuantumHarmonicOscillator()
    res = qho.multi_eigenstates(states=[0, 1, 2, 3], num_points=100)
    assert len(res["states"]) == 4
    for i, s in enumerate(res["states"]):
        assert s["n"] == i
        assert s["energy_nat"] == i + 0.5
        assert pytest.approx(qho.energy(i)) == s["energy"]
        assert pytest.approx(qho.classical_turning_point(i)) == s["x_tp"]
        assert len(s["psi"]) == 100
        assert len(s["prob"]) == 100

