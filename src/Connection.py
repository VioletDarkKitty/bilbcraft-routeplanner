class Connection:
    def __init__(self, weight: int, is_train: bool, label: str):
        self.connecting_locations = []
        self.weight = weight
        self.is_train = is_train
        self.label = label

    def add_location(self, location):
        self.connecting_locations.append(location)
        location.add_connection(self)

    def get_locations(self):
        return self.connecting_locations

    def get_is_train(self):
        return self.is_train

    def get_weight(self):
        return self.weight

    def get_label(self):
        return self.label

    def get_other_side(self, location):
        for loc in self.connecting_locations:
            if location.get_id() == loc.get_id():
                continue
            return loc
        return None
