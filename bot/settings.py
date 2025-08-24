from pathlib import Path
from typing import Any

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
config_path = BASE_DIR / 'config.yaml'

def load_config(path: Path) -> Any:
    with open(path) as f:
        return yaml.safe_load(f)

config = load_config(config_path)
