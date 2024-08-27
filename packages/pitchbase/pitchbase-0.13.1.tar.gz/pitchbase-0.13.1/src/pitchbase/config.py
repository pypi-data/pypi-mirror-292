import yaml
from . import constants


class Config:
    def __init__(self, cfg):
        self._cfg = cfg

    def __getattr__(self, k):
        v = self._cfg[k]
        if isinstance(v, dict):
            return Config(v)
        return v

    @staticmethod
    def read(path: str, profile: str):
        profile = profile or constants.DEFAULT_CONFIG_PROFILE
        c = yaml.safe_load(open(path, encoding="UTF-8").read()).get(profile)
        return Config(c)
