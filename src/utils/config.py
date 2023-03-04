import json

import yaml


class Config:
    def __init__(self, cfg: dict):
        for k, v in cfg.items():
            setattr(self, k, Config(v) if isinstance(v, dict) else v)

    def as_dict(self) -> dict:
        return json.loads(json.dumps(self, default=lambda o: getattr(o, "__dict__", str(o))))


def config_loader(config_file: str):
    config = yaml.safe_load(open(config_file))

    return Config(config)
