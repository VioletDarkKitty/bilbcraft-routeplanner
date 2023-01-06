import typing
from enum import Enum

from src.AStar import AStar, AStarPosition, AStarTimelimitException
from src.Location import Position, Location
from src.StorageProvider import StorageProvider


class Route:
    def __init__(self):
        self.entries = []

    def add_entry(self, entry):
        self.entries.append(entry)

    def get_entries(self):
        return self.entries


class RouteTimeoutException(Exception):
    pass


class RouteConnectionChanges(Enum):
    BoardTrain = 0
    LeaveTrain = 1
    ChangeTrain = 2
    EnterStreet = 3
    ChangeStreet = 4


class RoutePath:
    _cls_route_connection_changes_name_map = {
        RouteConnectionChanges.BoardTrain: "board_train",
        RouteConnectionChanges.LeaveTrain: "leave_train",
        RouteConnectionChanges.ChangeTrain: "change_train",
        RouteConnectionChanges.EnterStreet: "enter_street",
        RouteConnectionChanges.ChangeStreet: "change_street"
    }

    def __init__(self, from_position: AStarPosition, to_position: AStarPosition,
                 route_change: typing.Optional[RouteConnectionChanges], storage: StorageProvider,
                 stops: [AStarPosition]):
        self.from_position = from_position
        self.to_position = to_position
        self.route_change = route_change
        self.storage = storage
        self.train_ride_stops: [AStarPosition] = stops

    @staticmethod
    def _make_location_dict(location: Location):
        if location is None:
            return None

        data = {
            "label": location.get_label(),
            "position": location.get_pos()
        }

        return data

    def _make_position_dict(self, position: AStarPosition):
        data = {
            "position": position.pos,
            "location": self._make_location_dict(self.storage.get_location_at_pos(position.pos)),
        }
        if self.route_change in [RouteConnectionChanges.LeaveTrain, RouteConnectionChanges.ChangeTrain]:
            data["num_stops"] = len(self.train_ride_stops) + 1
            data["stops"] = [self._make_location_dict(self.storage.get_location_at_pos(x.pos))
                             for x in self.train_ride_stops]

        if self.route_change in [RouteConnectionChanges.BoardTrain, RouteConnectionChanges.ChangeTrain]:
            data["connection"] = {
                "label": position.connection.get_label(),
                "description": position.connection.get_description()
            }

        return data

    def to_dict(self) -> dict:
        if self.route_change in RoutePath._cls_route_connection_changes_name_map.keys():
            route_type = RoutePath._cls_route_connection_changes_name_map[self.route_change]
        else:
            route_type = "walk"

        data = {
            "type": route_type,
            "from": self._make_position_dict(self.from_position),
            "to": self._make_position_dict(self.to_position),
            "distance": AStar.distance_between_points(self.from_position.pos, self.to_position.pos)
        }

        return data

    def write_route_text(self) -> str:
        from_location = self.storage.get_location_at_pos(self.from_position.pos)
        to_location = self.storage.get_location_at_pos(self.to_position.pos)

        from_text = self.from_position.pos
        if from_location is not None:
            from_text = "{} ({})".format(from_text, from_location.get_label())
        to_text = self.to_position.pos
        if to_location is not None:
            to_text = "{} ({})".format(to_text, to_location.get_label())

        num_stops = len(self.train_ride_stops) + 1
        num_stops_text = "({} stop{})".format(num_stops, "" if num_stops == 1 else "s")

        if self.route_change == RouteConnectionChanges.BoardTrain:
            return "Board the {}".format(self.to_position.connection.label)
        elif self.route_change == RouteConnectionChanges.LeaveTrain:
            return "Leave the train at {} {}".format(to_text, num_stops_text)
        elif self.route_change == RouteConnectionChanges.ChangeTrain:
            return "Change trains at {} {} for the {}".format(to_text, num_stops_text, self.to_position.connection.label)
        else:
            return "Walk {} blocks from {} to {}".format(
                AStar.distance_between_points(self.from_position.pos, self.to_position.pos),
                from_text, to_text
            )

    def get_train_ride_stops(self):
        return self.train_ride_stops


class RoutePlanner:
    def __init__(self, storage: StorageProvider):
        self.storage = storage

    def plan_route(self, from_location: Position, to_location: Position, timelimit_ms: typing.Optional[int]) -> Route:
        astar = AStar(self.storage)
        try:
            path, cost = astar.get_path_to(from_location, to_location, timelimit_ms)
        except AStarTimelimitException:
            raise RouteTimeoutException()

        route_paths = self._make_paths_from_astar_points(path)
        route = Route()
        for path in route_paths:
            route.add_entry(path.to_dict())

        return route

    def _make_paths_from_astar_points(self, path) -> [RoutePath]:
        route_path = []

        current = None
        on_train = False
        train_riding_stops = []  # which stops do we go passed on the train, for plotting maps
        for position in path:
            if current is None:
                current = position

            if position.connection is not None:
                if position.connection.is_train:
                    if not on_train:
                        if current != position:
                            # walk to the station
                            route_path.append(RoutePath(current, position, None, self.storage, train_riding_stops))
                        # board train
                        route_path.append(RoutePath(position, position, RouteConnectionChanges.BoardTrain,
                                                    self.storage, train_riding_stops))
                        on_train = True
                        current = position
                        train_riding_stops = []
                    else:
                        if position.connection.label != current.connection.label:
                            # change trains
                            route_path.append(RoutePath(current, position, RouteConnectionChanges.ChangeTrain,
                                                        self.storage, train_riding_stops))
                            on_train = True
                            current = position
                            train_riding_stops = []
                        else:
                            train_riding_stops.append(position)
                else:
                    if current.connection is not None:
                        if current.connection.is_train:
                            # leave train
                            route_path.append(RoutePath(current, position, RouteConnectionChanges.LeaveTrain,
                                                        self.storage, train_riding_stops))
                            on_train = False
                            current = position
                            train_riding_stops = []
                        else:
                            # change to other connection (walking, street)
                            route_path.append(RoutePath(current, position, RouteConnectionChanges.ChangeStreet,
                                                        self.storage, train_riding_stops))
                            current = position
                    else:
                        # enter walking on connection (street)
                        route_path.append(RoutePath(current, position, RouteConnectionChanges.EnterStreet,
                                                    self.storage, train_riding_stops))
                        current = position
            else:
                if current.connection is not None:
                    if current.connection.is_train:
                        # leave train
                        route_path.append(RoutePath(current, position, RouteConnectionChanges.LeaveTrain, self.storage,
                                                    train_riding_stops))
                        on_train = False
                        current = position
                        train_riding_stops = []
                    else:
                        pass
                else:
                    pass

        if len(path) > 0:
            if current is not None and current.pos != path[-1].pos:
                route_path.append(RoutePath(current, path[-1], None, self.storage, train_riding_stops))

        return route_path
