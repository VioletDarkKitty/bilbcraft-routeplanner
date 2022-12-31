import typing
from enum import Enum

from src.AStar import AStar, AStarPosition
from src.Location import Position
from src.Route import Route, RouteEntry
from src.StorageProvider import StorageProvider


class RouteConnectionChanges(Enum):
    BoardTrain = 0
    LeaveTrain = 1
    ChangeTrain = 2


class RoutePath:
    def __init__(self, from_position: AStarPosition, to_position: AStarPosition,
                 route_change: typing.Optional[RouteConnectionChanges], storage: StorageProvider):
        self.from_position = from_position
        self.to_position = to_position
        self.route_change = route_change
        self.storage = storage

    def write_route_text(self) -> str:
        from_location = self.storage.get_location_at_pos(self.from_position.pos)
        to_location = self.storage.get_location_at_pos(self.to_position.pos)

        from_text = self.from_position.pos
        if from_location is not None:
            from_text = "{} ({})".format(from_text, from_location.get_label())
        to_text = self.to_position.pos
        if to_location is not None:
            to_text = "{} ({})".format(to_text, to_location.get_label())

        if self.route_change == RouteConnectionChanges.BoardTrain:
            return "Board the {}".format(self.to_position.connection.label)
        elif self.route_change == RouteConnectionChanges.LeaveTrain:
            return "Leave the train at {}".format(to_text)
        elif self.route_change == RouteConnectionChanges.ChangeTrain:
            return "Change trains"
        else:
            return "Walk {} blocks from {} to {}".format(
                AStar.distance_between_points(self.from_position.pos, self.to_position.pos),
                from_text, to_text
            )


class RoutePlanner:
    def __init__(self, storage: StorageProvider):
        self.storage = storage

    def plan_route(self, from_location: Position, to_location: Position) -> Route:
        astar = AStar(self.storage)
        path, cost = astar.get_path_to(from_location, to_location)

        route_paths = self._make_paths_from_astar_points(path)
        route = Route()
        for path in route_paths:
            route.add_entry(RouteEntry(path.write_route_text()))

        return route

    def _make_paths_from_astar_points(self, path) -> [RoutePath]:
        route_path = []

        current = None
        on_train = False
        for position in path:
            if current is None:
                current = position

            if position.connection is not None:
                if position.connection.is_train:
                    if not on_train:
                        if current != position:
                            # walk to the station
                            route_path.append(RoutePath(current, position, None, self.storage))
                        # board train
                        route_path.append(RoutePath(position, position, RouteConnectionChanges.BoardTrain,
                                                    self.storage))
                        on_train = True
                        current = position
                    else:
                        if position.connection.label != current.connection.label:
                            # change trains
                            route_path.append(RoutePath(current, position, RouteConnectionChanges.ChangeTrain,
                                                        self.storage))
                            on_train = True
                            current = position
                else:
                    pass
            else:
                if current.connection is not None:
                    if current.connection.is_train:
                        # leave train
                        route_path.append(RoutePath(position, position, RouteConnectionChanges.LeaveTrain,
                                                    self.storage))
                        on_train = False
                        current = position
                else:
                    pass

        if len(path) > 0:
            if current is not None and current.pos != path[-1].pos:
                route_path.append(RoutePath(current, path[-1], None, self.storage))

        return route_path