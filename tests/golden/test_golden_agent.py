from pathlib import Path
import pytest
from core.physics_engine import PhysicsEngine
from core.ai_agent import AIAgent

@pytest.fixture
def agent(tmp_path: Path):
    engine = PhysicsEngine(export_dir=tmp_path)
    return AIAgent(physics_engine=engine)

def test_parse_harmonic_oscillator(agent):
    parsed = agent.parse("harmonic oscillator n=4")
    assert parsed["action"] == "harmonic_oscillator"
    assert parsed["parameters"].get("n") == 4

@pytest.mark.xfail(reason="Known bug in regex chain: lone '?' does not match '\\b(help|\\?)\\b'")
def test_parse_lone_question_mark_help(agent):
    parsed = agent.parse("?")
    assert parsed["action"] == "help"
