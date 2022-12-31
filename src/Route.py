class RouteEntry:
    def __init__(self, entry_text: str, start_pos, end_pos, stops):
        self.entry_text = entry_text
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.train_ride_stops = stops

    def get_entry_text(self):
        return self.entry_text

    def get_start_pos(self):
        return self.start_pos

    def get_end_pos(self):
        return self.end_pos

    def get_train_ride_stops(self):
        return self.train_ride_stops


class Route:
    def __init__(self):
        self.entries = []

    def add_entry(self, entry: RouteEntry):
        self.entries.append(entry)

    def get_entries(self):
        return self.entries
