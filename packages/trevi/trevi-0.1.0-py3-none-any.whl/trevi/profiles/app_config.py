import yaml

class AppConfig:
    _config = {}

    def __init__(self, config) -> None:
        self._config = config

    @staticmethod
    def load(path):
        with open(path, "r") as stream:
            return AppConfig(yaml.safe_load(stream))

    def _get(self, path, config):
        if len(path) == 0:
            return config
        return self._get(path[1:], config[path[0]])

    def get(self, path: str) -> str | dict:
        return self._get(path.split("."), self._config)
