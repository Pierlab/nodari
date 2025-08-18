import json
from simulation.war import war_loader
from simulation.war.presets import DEFAULT_SIM_PARAMS


def test_load_sim_params_applies_overrides_and_defaults(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"parameters": {"unit_size": 42}}))
    params = war_loader.load_sim_params(str(path))
    assert params["unit_size"] == 42
    assert params["dispersion"] == DEFAULT_SIM_PARAMS["dispersion"]


def test_load_sim_params_missing_file(tmp_path):
    params = war_loader.load_sim_params(str(tmp_path / "missing.json"))
    assert params == DEFAULT_SIM_PARAMS
