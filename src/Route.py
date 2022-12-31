class RouteEntry:
    def __init__(self, entry_text: str):
        self.entry_text = entry_text

    def get_entry_text(self):
        return self.entry_text


class Route:
    def __init__(self):
        self.entries = []

    def add_entry(self, entry: RouteEntry):
        self.entries.append(entry)

    def get_entries(self):
        return self.entries
