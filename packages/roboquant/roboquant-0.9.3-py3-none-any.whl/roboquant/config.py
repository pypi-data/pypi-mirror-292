import os
import os.path
from configparser import ConfigParser


class Config:
    """Access to a roboquant configuration file.
    This allows sharing the same property file between both the Python and Kotlin
    version of roboquant.
    """

    def __init__(self, path=None):
        path = path or os.path.expanduser("~/.roboquant/.env")
        with open(path, "r", encoding="utf8") as f:
            config_string = "[default]\n" + f.read()
        self.config = ConfigParser()
        self.config.read_string(config_string)

    def get(self, key: str) -> str:
        for key2, value in os.environ.items():
            final_key = key2.lower().replace("_", ".")
            if final_key == key:
                return value
        return self.config.get("default", key)
