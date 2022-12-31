class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Position):
            return None
        return (self.x, self.y) == (other.x, other.y)

    def get_pos(self):
        return self.x, self.y


class Location(Position):
    from src.Connection import Connection

    def __init__(self, location_id, label: str, x: int, y: int):
        super().__init__(x, y)
        self.id = location_id
        self.label = label
        self.is_station = False
        self.connections = []

    def get_id(self):
        return self.id

    def add_connection(self, connection: Connection):
        self.connections.append(connection)
        if connection.is_train:
            self.is_station = True

    def get_label(self):
        return self.label

    def get_connections(self):
        return self.connections

    def get_is_station(self):
        return self.is_station
