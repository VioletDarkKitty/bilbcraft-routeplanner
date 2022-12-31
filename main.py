#
from src.Location import Position
from src.RoutePlanner import RoutePlanner
from src.StorageProvider import JsonStorageProvider

if __name__ == "__main__":
    storage = JsonStorageProvider("./data.json")
    planner = RoutePlanner(storage)

    above_central_station = Position(-200, -500)  # Position(-127, -283)
    above_tub_station = Position(392, -456)
    route = planner.plan_route(above_central_station, above_tub_station)

    for entry in route.get_entries():
        print(entry.get_entry_text())
