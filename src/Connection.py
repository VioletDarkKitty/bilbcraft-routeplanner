class Connection:
    def __init__(self, weight: int, is_train: bool, label: str, description: str):
        self.connecting_locations = []
        self.weight = weight
        self.is_train = is_train
        self.label = label
        self.description = description

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

    def set_weight(self, weight):
        self.weight = weight

    def set_is_train(self, is_train):
        self.is_train = is_train
        for location in self.connecting_locations:
            location.update_is_station()

    def set_label(self, label):
        self.label = label

    def remove_location(self, old_location):
        self.connecting_locations.remove(old_location)
        old_location.remove_connection(self)

    def get_description(self):
        return self.description if self.description is not None else ""

    def set_description(self, description):
        self.description = description
