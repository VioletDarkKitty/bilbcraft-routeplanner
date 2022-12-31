import json
import os.path
from enum import Enum

from src.StorageProvider import StorageProviderTypes


class ConfigException(Exception):
    pass


class ConfigKeys(Enum):
    StorageProviderType = "storage_provider_type"
    StorageProviderConfig = "storage_provider_config"
    WorldBorderDimensions = "world_border_dimensions"


class ConfigDataKeys(Enum):
    WorldBorderDimensionsMinX = "min_x"
    WorldBorderDimensionsMaxX = "max_x"
    WorldBorderDimensionsMinY = "min_y"
    WorldBorderDimensionsMaxY = "max_y"


class Config:
    def __init__(self, path):
        self.data = {
            ConfigKeys.StorageProviderType: StorageProviderTypes.JsonStorage,
            ConfigKeys.StorageProviderConfig: {
                "path": "./data.json"
            },
            ConfigKeys.WorldBorderDimensions: {
                ConfigDataKeys.WorldBorderDimensionsMinX: -10_000_000,
                ConfigDataKeys.WorldBorderDimensionsMaxX:  10_000_000,
                ConfigDataKeys.WorldBorderDimensionsMinY: -10_000_000,
                ConfigDataKeys.WorldBorderDimensionsMaxY:  10_000_000
            }
        }

        if os.path.exists(path):
            self.load_config(path)

    def get_config_value(self, key, default=None):
        if key in self.data.keys():
            return self.data[key]
        else:
            return default

    def load_config(self, path):
        with open(path, "r") as f:
            data = json.load(f)
            config_values = [x.value for x in ConfigKeys]
            for k, v in data.items():
                if k not in config_values:
                    raise ConfigException("Unknown config key {}".format(k))
                else:
                    self.data[k] = v
