from typing import Tuple


class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.prev_pos = None

    def __eq__(self, other):
        if not isinstance(other, Position):
            return None
        return (self.x, self.y) == (other.x, other.y)

    def get_pos(self):
        return self.x, self.y

    def get_prev_pos(self):
        return self.prev_pos

    def set_pos(self, pos: Tuple[int, int]):
        self.prev_pos = (self.x, self.y)
        self.x, self.y = pos

    def clear_prev_pos(self):
        self.prev_pos = None


class Location(Position):
    from src.Connection import Connection

    def __init__(self, location_id, label: str, x: int, y: int):
        super().__init__(x, y)
        self.id = location_id
        self.prev_id = None
        self.label = label
        self.is_station = False
        self.connections = []

    def get_id(self):
        return self.id

    def get_prev_id(self):
        return self.prev_id

    def clear_prev_id(self):
        self.prev_id = None

    def set_id(self, location_id):
        self.prev_id = self.id
        self.id = location_id

    def add_connection(self, connection: Connection):
        self.connections.append(connection)
        if connection.is_train:
            self.is_station = True

    def remove_connection(self, connection: Connection):
        self.connections.remove(connection)
        self.is_station = False
        self.update_is_station()

    def update_is_station(self):
        for connection in self.connections:
            if connection.is_train:
                self.is_station = True
                break

    def get_label(self):
        return self.label

    def set_label(self, label):
        self.label = label

    def get_connections(self):
        return self.connections

    def get_is_station(self):
        return self.is_station
