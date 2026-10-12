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


def test_cyclotron_resonance_and_energy(tmp_path):
    from quantum_cli.core.physics_engine import PhysicsEngine

    engine = PhysicsEngine(export_dir=tmp_path)
    data = engine.cyclotron_simulation(
        B_field=1.5,
        gap_voltage=50000.0,
        dee_radius=0.5,
    )

    # Resonance frequency for proton in 1.5 T field:
    # f_c = q*B / (2*pi*m) ≈ 1.602176634e-19 * 1.5 / (2 * pi * 1.67262192369e-27) ≈ 22.868 MHz
    assert pytest.approx(22.868, rel=1e-3) == data["cyclotron_frequency_mhz"]
    assert pytest.approx(143.682e6, rel=1e-3) == data["omega_c"]

    # Particles should accelerate to ~2.19 MeV over ~22-23 turns
    assert data["final_energy_mev"] > 2.0
    assert pytest.approx(2.194, rel=0.05) == data["final_energy_mev"]
    assert data["turns"] >= 20
    assert len(data["trajectory"][0]) > 100
    assert len(data["energy_mev"]) == len(data["t"])



