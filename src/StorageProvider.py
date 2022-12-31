import json
import math
import random
import typing
from abc import ABC, abstractmethod
from typing import Tuple

from src.Connection import Connection
from src.Direction import Direction


class StorageException(Exception):
    pass


class StorageProvider(ABC):
    def __init__(self):
        self.neighbour_directions = {
            Direction.North: (0, -1),
            Direction.South: (0, 1),
            Direction.West: (-1, 0),
            Direction.East: (1, 0),
            Direction.NE: (1, -1),
            Direction.NW: (-1, -1),
            Direction.SE: (1, 1),
            Direction.SW: (-1, 1)
        }

    @abstractmethod
    def get_locations(self):
        pass

    @abstractmethod
    def get_connections(self):
        pass

    @abstractmethod
    def get_pos_neighbours(self, pos: Tuple[int, int]):
        pass

    @abstractmethod
    def get_location_at_pos(self, pos: Tuple[int, int]):
        pass

    @abstractmethod
    def get_heuristic_distance_to_locations(self, current):
        pass


class Neighbour:
    def __init__(self, direction, pos: Tuple[int, int], connection):
        self.direction = direction
        self.pos = pos
        self.connection = connection


class JsonStorageProvider(StorageProvider):
    def __init__(self, path):
        super().__init__()
        self.locations = {}
        self.locations_by_position = {}
        self.locations_list = []
        self.connections = []

        with open(path, "r") as f:
            data = json.load(f)
            for key in ["locations", "connections"]:
                self._check_keys(key, data)

            for location_data in data["locations"]:
                for key in ["id", "label", "x", "y"]:
                    self._check_keys(key, location_data)
                from src.Location import Location
                location = Location(location_data["id"], location_data["label"], location_data["x"], location_data["y"])
                self.locations[location.get_id()] = location
                self.locations_by_position[location.get_pos()] = location
                self.locations_list.append(location)

            for connection_data in data["connections"]:
                for key in ["locations", "weight", "is_train", "label"]:
                    self._check_keys(key, connection_data)
                connection = Connection(connection_data["weight"], connection_data["is_train"],
                                        connection_data["label"])
                for connection_location in connection_data["locations"]:
                    if connection_location not in self.locations.keys():
                        raise StorageException("No such location '{}'".format(connection_location))
                    connection.add_location(self.locations[connection_location])
                self.connections.append(connection)

    def get_locations(self):
        return self.locations_list

    def get_connections(self):
        return self.connections

    def get_pos_neighbours(self, pos: Tuple[int, int]) -> [Neighbour]:
        neighbours = []
        x, y = pos
        for direction, neighbour_direction in self.neighbour_directions.items():
            nx, ny = neighbour_direction
            x2 = x + nx
            y2 = y + ny
            if not self._is_within_world((x2, y2)):
                continue
            neighbours.append(Neighbour(direction, (x2, y2), None))

        location = self.get_location_at_pos(pos)
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

    def get_heuristic_distance_to_locations(self, pos: Tuple[int, int]) -> typing.Optional[int]:
        """
        Check 1/8th of the locations we know about randomly, if they are a train then return the shortest distance
        :param pos: Position to check
        :return: The shortest distance to a train that we checked
        """
        checking_locations = {}
        checking_num = math.ceil(len(self.locations_list) / 8)
        while checking_num > 0:
            next_check_pos = random.randint(0, len(self.locations_list) - 1)
            if next_check_pos in checking_locations.keys():
                continue
            checking_locations[next_check_pos] = self.locations_list[next_check_pos]
            checking_num -= 1

        min_distance = None
        for _, v in checking_locations.items():
            if not v.get_is_station():
                continue

            from src.AStar import AStar
            dist = AStar.distance_between_points(pos, v.get_pos())
            if min_distance is None or dist < min_distance:
                min_distance = dist

        return min_distance

    @staticmethod
    def _check_keys(key, data):
        if key not in data.keys():
            raise StorageException("Key '{}' missing in json data".format(key))

    @staticmethod
    def _is_within_world(_):
        return True
