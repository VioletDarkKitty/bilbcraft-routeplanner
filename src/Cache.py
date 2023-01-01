import multiprocessing
import mgzip
import json
import typing


class Cache:
    def __init__(self):
        self.data = {}

    def from_file(self, path):
        with open(path, "rb") as f:
            with mgzip.open(f, "rt", thread=multiprocessing.cpu_count()) as gz:
                self.data = json.load(gz)

    def to_file(self, path):
        with open(path, "wb") as f:
            with mgzip.open(f, "wt", thread=multiprocessing.cpu_count()) as gz:
                json.dump(self.data, gz)

    def set_cached_value(self, cache_type: str, cache_key: str, cache_value):
        if cache_type not in self.data.keys():
            self.data[cache_type] = {}
        self.data[cache_type][cache_key] = cache_value

    def get_cached_value(self, cache_type: str, cache_key: str) -> typing.Optional[typing.Any]:
        if cache_type not in self.data.keys() or cache_key not in self.data[cache_type].keys():
            return None
        return self.data[cache_type][cache_key]
