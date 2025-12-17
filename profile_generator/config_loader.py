
from pathlib import Path
import yaml

def load_profile_config(yaml_path: str) -> dict:
    path = Path(yaml_path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r") as f:
        cfg = yaml.safe_load(f)

    if "profilegenerator_config" not in cfg:
        raise KeyError("Missing 'profilegenerator_config' in YAML")

    return cfg["profilegenerator_config"]
