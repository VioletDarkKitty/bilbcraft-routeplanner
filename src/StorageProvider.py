import gc
import json
import math
import os.path
import random
import typing
from abc import ABC, abstractmethod
from enum import Enum
from multiprocessing.pool import ThreadPool, Pool
from typing import Tuple

from src.Cache import Cache
from src.Connection import Connection
from src.Direction import Direction
from src.Location import Location
from src.Logger import Logger, LogEntry, LogLevel


class StorageException(Exception):
    pass


class StorageProviderTypes(Enum):
    JsonStorage = "json"


class StorageProvider(ABC):
    def __init__(self, logger: Logger):
        self.logger = logger

        self.neighbour_directions = {
            Direction.North: (0, -1),
            Direction.South: (0, 1),
            Direction.West: (-1, 0),
            Direction.East: (1, 0)
        }
        """Direction.NE: (1, -1),
            Direction.NW: (-1, -1),
            Direction.SE: (1, 1),
            Direction.SW: (-1, 1)"""

    @staticmethod
    def create(logger: Logger, provider_type, data):
        provider_types = {
            StorageProviderTypes.JsonStorage: JsonStorageProvider
        }
        if provider_type in provider_types:
            return provider_types[provider_type](logger, **data)
        else:
            raise StorageException("Unknown storage type {}".format(provider_type))

    def get_logger(self) -> Logger:
        return self.logger

    @staticmethod
    def update_storage_version(self, old_version: typing.Optional[int], new_version: int):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def get_locations(self):
        pass

    @abstractmethod
    def add_location(self, location: Location):
        pass

    @abstractmethod
    def delete_location(self, location: Location):
        pass

    @abstractmethod
    def get_connections(self):
        pass

    @abstractmethod
    def add_connection(self, connection: Connection):
        pass

    @abstractmethod
    def delete_connection(self, connection: Connection):
        pass

    @abstractmethod
    def get_pos_neighbours(self, pos: Tuple[int, int]):
        pass

    @abstractmethod
    def get_location_at_pos(self, pos: Tuple[int, int]) -> Location:
        pass

    @abstractmethod
    def get_location_by_id(self, location_id):
        pass

    @abstractmethod
    def get_heuristic_distance_to_locations(self, current):
        pass

    @staticmethod
    def _is_within_world(_):
        return True

    @abstractmethod
    def update_location(self, location):
        pass

    @abstractmethod
    def update_connection(self, connection):
        pass

    @abstractmethod
    def make_cache(self, min_x: int, max_x: int, min_y: int, max_y: int, max_threads: int,
                   callback: typing.Callable[[int], None]):
        pass


class Neighbour:
    def __init__(self, direction, pos: Tuple[int, int], connection):
        self.direction = direction
        self.pos = pos
        self.connection = connection

    def to_dict(self, original_location):
        return {
            "pos": self.pos
        }

    @staticmethod
    def from_dict(data):
        Neighbour(0, data["pos"], None)


class JsonStorageProvider(StorageProvider):
    def __init__(self, logger: Logger, path):
        super().__init__(logger)
        self.version: int = 1
        self.path = path
        self.locations_by_id = {}
        self.locations_by_position = {}
        self.locations_list = []
        self.connections = []
        self.cache_path = "./cache.dat.gz"
        self.cache = Cache()
        if os.path.exists(self.cache_path):
            print("Loading from cache")
            self.cache.from_file(self.cache_path)

        with open(path, "r") as f:
            data = json.load(f)

            # updating the data does not load it but does modify it
            save_required = False
            if "version" not in data or data["version"] < self.version:
                old_version = data["version"] if "version" in data.keys() else None
                self.update_storage_version(old_version, self.version, data)
                save_required = True

            self.load_json_data(data)
            if save_required:
                self.save()

    def update_storage_version(self, old_version: typing.Optional[int], new_version: int, data):
        if old_version is None:
            data["version"] = self.version
            self.load_json_data(data, allow_default_fill=True, no_object_construction=True)
        else:
            raise StorageException("Cannot upgrade from version {} to {}".format(old_version, new_version))
        self.logger.add_entry(LogEntry.create(LogLevel.Info,
                                              "Updated storage from version {} to {}".format(old_version, new_version)))

    def load_json_data(self, data, allow_default_fill=False, no_object_construction=False):
        for key in ["locations", "connections"]:
            self._check_keys(key, data, allow_default_fill)
        for location_data in data["locations"]:
            for key in ["id", "label", "x", "y", "description"]:
                self._check_keys(key, location_data, allow_default_fill)
            if not no_object_construction:
                from src.Location import Location
                location = Location(location_data["id"], location_data["label"], location_data["x"], location_data["y"],
                                    location_data["description"])
                self.locations_by_id[location.get_id()] = location
                self.locations_by_position[location.get_pos()] = location
                self.locations_list.append(location)
        for connection_data in data["connections"]:
            for key in ["locations", "weight", "is_train", "label", "description"]:
                self._check_keys(key, connection_data, allow_default_fill)
            if not no_object_construction:
                connection = Connection(connection_data["weight"], connection_data["is_train"],
                                        connection_data["label"], connection_data["description"])
                for connection_location in connection_data["locations"]:
                    if connection_location not in self.locations_by_id.keys():
                        raise StorageException("No such location '{}'".format(connection_location))
                    connection.add_location(self.locations_by_id[connection_location])
                self.connections.append(connection)

    def save(self):
        data = {
            "version": self.version,
            "locations": [],
            "connections": []
        }

        for location in self.get_locations():
            x, y = location.get_pos()
            location_data = {
                "id": location.get_id(),
                "label": location.get_label(),
                "x": x,
                "y": y,
                "description": location.get_description()
            }
            data["locations"].append(location_data)

        for connection in self.get_connections():
            connection_data = {
                "locations": [x.get_id() for x in connection.get_locations()],
                "weight": connection.get_weight(),
                "is_train": connection.get_is_train(),
                "label": connection.get_label(),
                "description": connection.get_description()
            }
            data["connections"].append(connection_data)

        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)

    def get_locations(self):
        return self.locations_list

    def get_connections(self):
        return self.connections

    def get_pos_neighbours(self, pos: Tuple[int, int]) -> [Neighbour]:
        cached_value = self.cache.get_cached_value("neighbours", str(pos))
        if cached_value is not None:
            neighbours = [Neighbour.from_dict(x) for x in cached_value]
            neighbours.extend(self._get_neighbours_for_location(pos))
            return neighbours

        neighbours = []
        x, y = pos
        for direction, neighbour_direction in self.neighbour_directions.items():
            nx, ny = neighbour_direction
            x2 = x + nx
            y2 = y + ny
            if not self._is_within_world((x2, y2)):
                continue
            neighbours.append(Neighbour(direction, (x2, y2), None))

        neighbours.extend(self._get_neighbours_for_location(pos))

        return neighbours

    def _get_neighbours_for_location(self, pos):
        location = self.get_location_at_pos(pos)
        neighbours = []
        if location is not None:
            for connection in location.get_connections():
                other_location = connection.get_other_side(location)
                if other_location is not None:
                    neighbours.append(Neighbour(None, other_location.get_pos(), connection))
        return neighbours

    def get_location_at_pos(self, pos: Tuple[int, int]):
        if pos in self.locations_by_position.keys():
            return self.locations_by_position[pos]
        return None

    def get_location_by_id(self, location_id):
        if location_id in self.locations_by_id.keys():
            return self.locations_by_id[location_id]
        return None

    def get_heuristic_distance_to_locations(self, pos: Tuple[int, int]) -> typing.Optional[int]:
        """
        Check 1/8th of the locations we know about randomly, if they are a train then return the shortest distance
        :param pos: Position to check
        :return: The shortest distance to a train that we checked
        """
        cached_value = self.cache.get_cached_value("heuristic", str(pos))
        if cached_value is not None:
            return cached_value

        checking_locations = {}
        checking_num = math.ceil(len(self.locations_list) / 8)
        while checking_num > 0:
            next_check_pos = random.randint(0, len(self.locations_list) - 1)
            if next_check_pos in checking_locations.keys():
                continue
            checking_locations[next_check_pos] = self.locations_list[next_check_pos]
            checking_num -= 1

        return self._get_min_distance_to_locations(list(checking_locations.values()), pos)

    @staticmethod
    def _get_min_distance_to_locations(checking_locations, pos):
        min_distance = None
        for v in checking_locations:
            if not v.get_is_station():
                continue

            from src.AStar import AStar
            dist = AStar.distance_between_points(pos, v.get_pos())
            if min_distance is None or dist < min_distance:
                min_distance = dist
        return min_distance

    @staticmethod
    def _check_keys(key, data, default_if_missing=False, default=None):
        if key not in data.keys():
            if default_if_missing:
                data[key] = default
            else:
                raise StorageException("Key '{}' missing in json data".format(key))

    def add_location(self, location: Location):
        self.locations_by_id[location.get_id()] = location
        self.locations_by_position[location.get_pos()] = location
        self.locations_list.append(location)

    def delete_location(self, location: Location):
        del self.locations_by_id[location.get_id()]
        del self.locations_by_position[location.get_pos()]
        self.locations_list.remove(location)
        for connection in location.get_connections():
            self.delete_connection(connection)

    def add_connection(self, connection: Connection):
        self.connections.append(connection)

    def delete_connection(self, connection: Connection):
        self.connections.remove(connection)
        for location in connection.get_locations():
            location.remove_connection(connection)

    def update_location(self, location):
        if location.get_prev_id() is not None:
            del self.locations_by_id[location.get_prev_id()]
            location.clear_prev_id()
        if location.get_prev_pos() is not None:
            del self.locations_by_position[location.get_prev_pos()]
            location.clear_prev_pos()
        self.locations_by_id[location.get_id()] = location
        self.locations_by_position[location.get_pos()] = location

    def update_connection(self, connection):
        pass

    def _make_cache_job(self, pos):
        locations = self.get_locations()
        return pos, self._get_min_distance_to_locations(locations, pos), []

    @staticmethod
    def _square_generator(min_x, max_x, min_y, max_y):
        for i in range(min_x, max_x + 1):
            for j in range(min_y, max_y + 1):
                yield i, j

    @staticmethod
    def _chunk_array(array, chunk_size):
        for i in range(0, len(array), chunk_size):
            yield array[i:i + chunk_size]

    def make_cache(self, min_x: int, max_x: int, min_y: int, max_y: int, max_threads: int,
                   callback: typing.Callable[[int], None]):
        pool = Pool(max_threads)

        positions = list(self._square_generator(min_x, max_x, min_y, max_y))
        results_set = []
        gc_every = 1000
        last_gc = 0
        for i, data_part in enumerate(self._chunk_array(positions, 1000000)):
            results = pool.map(self._make_cache_job, data_part)
            results_set.append(results)
            if last_gc >= gc_every:
                print("gc")
                gc.collect()
                last_gc = 0
            last_gc += 1

            callback(i * 1000)
        pool.close()
        pool.terminate()

        for results in results_set:
            for result in results:
                pos, heuristic, neighbours = result
                self.cache.set_cached_value("heuristic", str(pos), heuristic)
                # self.cache.set_cached_value("neighbours", str(pos), neighbours)

        self.cache.to_file(self.cache_path)
