import yaml
from .utils import load_safe_json, get_path_level, JSONType


def load_config(config_path: str, settings_path: str) -> JSONType:
    config_level = get_path_level(config_path)
    settings_level = get_path_level(settings_path) - 1

    if config_level >= settings_level:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    else:
        return load_safe_json(settings_path)
