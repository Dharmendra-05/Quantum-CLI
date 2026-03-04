"""
AI Agent Module
Simulates natural language parsing to map user commands to physics engine functions.
"""

import re
import logging
from typing import Any, Dict, Optional, Tuple
from core.physics_engine import PhysicsEngine

logger = logging.getLogger(__name__)


class AIAgent:
    """
    Interprets natural language commands and invokes appropriate physics methods.
    Uses rule-based pattern matching to simulate an AI.
    """

    def __init__(self, physics_engine: PhysicsEngine):
        self.physics = physics_engine
        self.command_history = []

    def parse(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user input and return a structured command.

        Args:
            user_input: Raw string from CLI.

        Returns:
            Dictionary with keys:
                - 'action': string identifier (e.g., 'harmonic_oscillator', 'kss_bound', 'help', 'exit')
                - 'parameters': dict of extracted parameters
                - 'confidence': float between 0 and 1 (simulated)
                - 'original_input': the raw input
        """
        user_input = user_input.strip()
        self.command_history.append(user_input)

        # Normalize: lowercase and remove extra spaces
        normalized = re.sub(r"\s+", " ", user_input.lower())

        # Default response
        response = {
            "action": "unknown",
            "parameters": {},
            "confidence": 0.0,
            "original_input": user_input,
        }

        # Help
        if re.search(r"\b(help|\?)\b", normalized):
            response["action"] = "help"
            response["confidence"] = 1.0
            return response

        # Exit
        if re.search(r"\b(exit|quit|bye)\b", normalized):
            response["action"] = "exit"
            response["confidence"] = 1.0
            return response

        # Harmonic oscillator
        ho_patterns = [
            r"(harmonic|oscillator|qho)",
            r"(wavefunction|probability)",
        ]
        if any(re.search(p, normalized) for p in ho_patterns):
            response["action"] = "harmonic_oscillator"
            response["confidence"] = 0.9
            # Extract quantum number n
            n_match = re.search(r"n\s*=\s*(\d+)", normalized)
            if not n_match:
                n_match = re.search(r"level\s+(\d+)", normalized)
            if n_match:
                response["parameters"]["n"] = int(n_match.group(1))
            else:
                response["parameters"]["n"] = 0  # default

            # Extract position range
            range_match = re.search(r"range\s+([-+]?\d*\.?\d+)\s+to\s+([-+]?\d*\.?\d+)", normalized)
            if range_match:
                response["parameters"]["x_min"] = float(range_match.group(1))
                response["parameters"]["x_max"] = float(range_match.group(2))
            else:
                response["parameters"]["x_min"] = -5.0
                response["parameters"]["x_max"] = 5.0

            return response

        # KSS bound / QCD
        kss_patterns = [
            r"(kss|kovtun|son|starinets|bound)",
            r"(qcd|quark|gluon|plasma)",
        ]
        if any(re.search(p, normalized) for p in kss_patterns):
            response["action"] = "kss_bound"
            response["confidence"] = 0.85
            # Check if user wants sample data
            if re.search(r"(sample|data|hypothetical)", normalized):
                response["parameters"]["sample_data"] = True
            else:
                response["parameters"]["sample_data"] = False
            return response

        return response

    def execute(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the parsed command using the physics engine.

        Args:
            parsed: Output from parse() method.

        Returns:
            Result dictionary with at least 'success' and 'message' keys.
        """
        action = parsed["action"]
        params = parsed["parameters"]

        if action == "help":
            return {
                "success": True,
                "message": "Available commands:\n"
                "  - Harmonic oscillator: 'harmonic oscillator n=2'\n"
                "  - KSS bound: 'show KSS bound with sample data'\n"
                "  - Exit: 'exit' or 'quit'\n"
                "  - Help: 'help'",
                "data": None,
            }

        if action == "exit":
            return {"success": True, "message": "Exiting...", "data": None}

        if action == "harmonic_oscillator":
            try:
                n = params.get("n", 0)
                x_min = params.get("x_min", -5.0)
                x_max = params.get("x_max", 5.0)
                result = self.physics.harmonic_oscillator_wavefunction(
                    n=n, x_range=(x_min, x_max), save_plot=True
                )
                msg = f"Harmonic oscillator n={n}: Energy = {result['energy']:.3e} J"
                if result["plot_path"]:
                    msg += f"\nPlot saved to: {result['plot_path']}"
                return {"success": True, "message": msg, "data": result}
            except Exception as e:
                logger.exception("Error in harmonic oscillator")
                return {"success": False, "message": f"Error: {str(e)}", "data": None}

        if action == "kss_bound":
            try:
                sample = params.get("sample_data", False)
                result = self.physics.kss_bound(generate_sample_data=sample, save_plot=True)
                bound = result["bound_value"]
                msg = f"KSS bound: η/s ≥ {bound:.3e} K·s"
                if result["plot_path"]:
                    msg += f"\nPlot saved to: {result['plot_path']}"
                return {"success": True, "message": msg, "data": result}
            except Exception as e:
                logger.exception("Error in KSS bound")
                return {"success": False, "message": f"Error: {str(e)}", "data": None}

        # Unknown action
        return {
            "success": False,
            "message": f"Sorry, I didn't understand: '{parsed['original_input']}'. Type 'help' for options.",
            "data": None,
        }