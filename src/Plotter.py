import matplotlib.pyplot as plt
from matplotlib import LineCollection
import numpy as np

from RoutePlanner import Route
from StorageProvider import StorageProvider


class Plotter(object):
    @staticmethod
    def plot_routemap(planned_route: Route, storage: StorageProvider):
        fig, ax = plt.subplots()

        fig.set_size_inches(100, 100)

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
        fig.savefig("output.png")
