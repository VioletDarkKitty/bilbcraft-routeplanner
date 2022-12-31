#
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

from src.Location import Position
from src.RoutePlanner import RoutePlanner
from src.StorageProvider import JsonStorageProvider

if __name__ == "__main__":
    storage = JsonStorageProvider("./data.json")
    planner = RoutePlanner(storage)

    above_central_station = Position(-1000, -500)  # Position(-127, -283)
    #start_pos = Position(-1000, 200)
    above_tub_station = Position(392, -456)
    route = planner.plan_route(above_central_station, above_tub_station)

    for entry in route.get_entries():
        print(entry.get_entry_text())

    fig, ax = plt.subplots()

    lines = []
    for connection in storage.get_connections():
        a, b = connection.get_locations()
        line = [(a.get_pos()[0], -a.get_pos()[1]), (b.get_pos()[0], -b.get_pos()[1])]
        lines.append(line)
    ax.add_collection(LineCollection(lines, colors=np.array([(0.0, 0.1, 0.5, 0.8)]), linewidths=4))

    landmark_xs = []
    landmark_ys = []
    landmark_labels = []
    for location in storage.get_locations():
        landmark_xs.append(location.get_pos()[0])
        landmark_ys.append(-location.get_pos()[1])
        landmark_labels.append(location.get_label())
    ax.scatter(landmark_xs, landmark_ys)
    for i, txt in enumerate(landmark_labels):
        ax.annotate(txt, (landmark_xs[i], landmark_ys[i]))

    route_xs = []
    route_ys = []
    for entry in route.get_entries():
        route_xs.append(entry.get_start_pos()[0])
        route_ys.append(-entry.get_start_pos()[1])

        for stop_location in entry.get_train_ride_stops():
            stop_pos = stop_location.pos
            route_xs.append(stop_pos[0])
            route_ys.append(-stop_pos[1])

        route_xs.append(entry.get_end_pos()[0])
        route_ys.append(-entry.get_end_pos()[1])
    ax.plot(route_xs, route_ys, color="red")

    plt.savefig("output.png")
