#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
import sys

from src.Config import Config, ConfigKeys
from src.Location import Position
from src.RoutePlanner import RoutePlanner
from src.StorageProvider import StorageProvider
from src.Editor import EditorApplication


class Application:
    def __init__(self):
        self.config = Config("./config.json")
        self.storage = StorageProvider.create(
            self.config.get_config_value(ConfigKeys.StorageProviderType),
            self.config.get_config_value(ConfigKeys.StorageProviderConfig)
        )

        use_editor = "editor" in sys.argv[1:] if len(sys.argv) > 1 else False
        if use_editor:
            EditorApplication(self.storage, self.config).run()
        else:
            planner = RoutePlanner(self.storage)

            above_central_station = Position(87, -220)  # Position(-127, -283)
            # start_pos = Position(-1000, 200)
            above_tub_station = Position(1566, -288)
            route = planner.plan_route(above_central_station, above_tub_station)

            for entry in route.get_entries():
                print(entry.get_entry_text())

            self.plot_routemap(route)

    def plot_routemap(self, planned_route):
        fig, ax = plt.subplots()

        lines = []
        for connection in self.storage.get_connections():
            a, b = connection.get_locations()
            line = [(a.get_pos()[0], -a.get_pos()[1]), (b.get_pos()[0], -b.get_pos()[1])]
            lines.append(line)
        ax.add_collection(LineCollection(lines, colors=np.array([(0.0, 0.1, 0.5, 0.8)]), linewidths=4))

        landmark_xs = []
        landmark_ys = []
        landmark_labels = []
        for location in self.storage.get_locations():
            landmark_xs.append(location.get_pos()[0])
            landmark_ys.append(-location.get_pos()[1])
            landmark_labels.append(location.get_label())
        ax.scatter(landmark_xs, landmark_ys)
        for i, label in enumerate(landmark_labels):
            ax.annotate(label, (landmark_xs[i], landmark_ys[i]))

        route_poss = []
        for entry in planned_route.get_entries():
            route_poss.append([entry.get_start_pos()[0], -entry.get_start_pos()[1]])

            for stop_location in entry.get_train_ride_stops():
                stop_pos = stop_location.pos
                route_poss.append([stop_pos[0], -stop_pos[1]])

            route_poss.append([entry.get_end_pos()[0], -entry.get_end_pos()[1]])
        point_pairs = [(route_poss[i], route_poss[i + 1]) for i in range(len(route_poss)) if i < len(route_poss) - 1]
        ax.add_collection(LineCollection(point_pairs, colors=np.array([(1, 0, 0, 1)]), linewidths=1))

        ax.autoscale()
        plt.savefig("output.png")


if __name__ == "__main__":
    Application()
