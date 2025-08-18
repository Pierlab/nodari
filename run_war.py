"""Entry point for the war simulation viewer."""
from simulation.war.viewer_loop import run
from simulation.war.war_loader import load_sim_params, _spawn_armies, sim_params

__all__ = ["load_sim_params", "_spawn_armies", "sim_params", "run"]

if __name__ == "__main__":  # pragma: no cover - manual launch
    run()
