#!/usr/bin/python3
import gzip
import sys
import time
import traceback

from src.Config import Config, ConfigKeys
from src.Editor import EditorApplication
from src.Logger import Logger, LogEntry, LogLevel
from src.ServerNetworkInterface import ServerNetworkInterface, ClientNetworkInterface
from src.StorageProvider import StorageProvider


class Application:
    def __init__(self):
        self.config = Config("./config.json")
        self.logger = Logger.create(
            self.config.get_config_value(ConfigKeys.LoggerType),
            self.config.get_config_value(ConfigKeys.LoggerConfig)
        )
        print("Loading from storage")
        self.storage = StorageProvider.create(
            self.logger,
            self.config.get_config_value(ConfigKeys.StorageProviderType),
            self.config.get_config_value(ConfigKeys.StorageProviderConfig)
        )

        args = sys.argv[1:]
        self.use_editor = "editor" in args if len(sys.argv) > 1 else False
        self.as_client = "client" in args if len(sys.argv) > 1 else False

    def run(self):
        try:
            if self.use_editor:
                EditorApplication(self.storage, self.config).run()
            elif self.as_client:
                ClientNetworkInterface(self.config, self.storage).run()
            else:
                """planner = RoutePlanner(self.storage)
    
                from_pos = Position(87, -220)
                to_pos = Position(12177, -256)
                route = planner.plan_route(from_pos, to_pos)
    
                for entry in route.get_entries():
                    print(entry.get_entry_text())
    
                self.plot_routemap(route)"""
                ServerNetworkInterface(self.config, self.storage).run()
        except Exception as _e:
            self.logger.add_entry(LogEntry.create(LogLevel.Fatal, traceback.format_exc()))
            raise _e


if __name__ == "__main__":
    profile = "profile" in sys.argv[1:] if len(sys.argv) > 1 else False

    if profile:
        import cProfile
        from pycallgraph2 import PyCallGraph, GlobbingFilter, Config as PyCallGraphConfig
        from pycallgraph2.output import GraphvizOutput
        import pstats
        import io

        config = PyCallGraphConfig(max_depth=8)
        config.trace_filter = GlobbingFilter(exclude=[
            "pycallgraph.*",
            "matplotlib.*"
        ])

        output_name = str(time.time()) + ".dat.gz"
        profiler = cProfile.Profile()
        with PyCallGraph(output=GraphvizOutput(), config=config):
            profiler.enable()
            try:
                Application().run()
            except Exception as e:
                print(traceback.format_exc())
        profiler.disable()

        output_buffer = io.StringIO()
        ps = pstats.Stats(profiler, stream=output_buffer).sort_stats('tottime')
        ps.print_stats()

        with open(output_name, "wb") as f:
            with gzip.open(f, "wt") as gz:
                gz.write(output_buffer.getvalue())
    else:
        Application().run()
