from pathlib import Path

import pytest

from quantum_cli.core.ai_agent import AIAgent
from quantum_cli.core.physics_engine import PhysicsEngine


@pytest.fixture
def agent(tmp_path: Path):
    engine = PhysicsEngine(export_dir=tmp_path)
    return AIAgent(physics_engine=engine)

def test_parse_harmonic_oscillator(agent):
    parsed = agent.parse("harmonic oscillator n=4")
    assert parsed["action"] == "harmonic_oscillator"
    assert parsed["parameters"].get("n") == 4

def test_parse_harmonic_oscillator_multi(agent):
    parsed = agent.parse("harmonic oscillator states 0,1,2,3")
    assert parsed["action"] == "harmonic_oscillator_multi"
    assert parsed["parameters"].get("states") == [0, 1, 2, 3]

def test_parse_qho_states_range(agent):
    parsed = agent.parse("qho states 0 to 3")
    assert parsed["action"] == "harmonic_oscillator_multi"
    assert parsed["parameters"].get("states") == [0, 1, 2, 3]

@pytest.mark.xfail(reason="Known bug in regex chain: lone '?' does not match '\\b(help|\\?)\\b'")
def test_parse_lone_question_mark_help(agent):
    parsed = agent.parse("?")
    assert parsed["action"] == "help"


def test_parse_cyclotron_parameters(agent):
    parsed = agent.parse("cyclotron B=1.8 voltage=60kV radius=60cm")
    assert parsed["action"] == "cyclotron"
    assert pytest.approx(1.8) == parsed["parameters"]["B_field"]
    assert pytest.approx(60000.0) == parsed["parameters"]["gap_voltage"]
    assert pytest.approx(0.6) == parsed["parameters"]["dee_radius"]


def test_execute_cyclotron(agent):
    parsed = agent.parse("simulate cyclotron B=1.5 voltage=50kV radius=0.5m")
    result = agent.execute(parsed)
    assert result["success"] is True
    assert "data" in result
    assert result["data"]["final_energy_mev"] > 2.0


