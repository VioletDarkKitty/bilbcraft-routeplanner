import datetime
import heapq
import math
import typing

from src.Location import Position
from src.StorageProvider import StorageProvider


class AStarTimelimitException(Exception):
    pass


class AStarPosition:
    def __init__(self, pos, connection):
        self.pos = pos
        self.connection = connection


class AStar:
    def __init__(self, storage: StorageProvider):
        self.storage = storage
        self.heuristic_distance_threshold = 2000

    def get_path_to(self, start_pos: Position, end_pos: Position, timelimit_ms: typing.Optional[int]):
        node_heap = []
        heapq.heappush(node_heap, (0, start_pos.get_pos()))
        node_map = {
            start_pos.get_pos(): None
        }
        costs = {
            start_pos.get_pos(): 0
        }
        begin_time = datetime.datetime.now()
        timelimit_seconds = timelimit_ms / 1000
        while not node_heap == []:
            if timelimit_ms is not None and (datetime.datetime.now() - begin_time).total_seconds() > timelimit_seconds:
                raise AStarTimelimitException()

            current = heapq.heappop(node_heap)[1]

            if current == end_pos.get_pos():
                break

            for neighbour in self.storage.get_pos_neighbours(current):
                next_pos = neighbour.pos

                #if next_pos != start_pos.get_pos(): #and not self.can_enter_tile(next_pos, game, direction,
                                        #                        ignore_entities=ignore_entities):
                #    continue

                min_station_dist = self.storage.get_heuristic_distance_to_locations(current)
                additional_cost = self.distance_between_points(current, next_pos)
                if min_station_dist < self.heuristic_distance_threshold:
                    additional_cost = 10
                elif neighbour.connection is not None:
                    if neighbour.connection.is_train:
                        additional_cost /= 1000
                    additional_cost += neighbour.connection.get_weight()
                new_cost = costs.get(current) + additional_cost
                if next_pos not in costs or new_cost < costs[next_pos]:
                    costs[next_pos] = new_cost
                    priority = new_cost + self.distance_between_points(next_pos, end_pos.get_pos())
                    heapq.heappush(node_heap, (priority, next_pos))
                    node_map[next_pos] = AStarPosition(current, neighbour.connection)

        path = []
        if end_pos.get_pos() not in node_map.keys():
            return None, costs
        current = node_map[end_pos.get_pos()]
        while current is not None:
            path.append(current)
            current = node_map[current.pos]
        path.reverse()

        return path, costs

    @staticmethod
    def distance_between_points(a, b):
        x1, y1 = a
        x2, y2 = b

        # return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        # use Manhattan distance instead, less priority for diagonal distances
        return abs(x2 - x1) + abs(y2 - y1)
