import asyncio
import json
from json import JSONDecodeError

from src.Config import Config, ConfigKeys, ConfigDataKeys
from src.Location import Position
from src.RoutePlanner import RoutePlanner
from src.StorageProvider import StorageProvider


class NetworkProtocol(asyncio.Protocol):
    def __init__(self, interface):
        self.transport = None
        self.interface = interface

    def connection_made(self, transport):
        peer_name = transport.get_extra_info('peername')
        print('Connection from {}'.format(peer_name))
        self.transport = transport

    def report_invalid(self):
        self.transport.write(json.dumps({
            "error": "Invalid"
        }).encode())

    def data_received(self, data):
        message = data.decode()
        print('Data received: {!r}'.format(message))

        try:
            json_data = json.loads(message)
        except JSONDecodeError:
            self.report_invalid()
            self.transport.close()
            return

        if isinstance(json_data, dict) and "type" in json_data.keys():
            if json_data["type"] == "route":
                for v in ["x1", "x2", "y1", "y2"]:
                    if v not in json_data.keys() or not isinstance(json_data[v], int):
                        self.report_invalid()
                        self.transport.close()
                        return
                pos1 = Position(json_data["x1"], json_data["y1"])
                pos2 = Position(json_data["x2"], json_data["y2"])

                route = self.interface.planner.plan_route(pos1, pos2)
                data = []
                for entry in route.get_entries():
                    data.append(entry.get_entry_text())
                self.transport.write(json.dumps(data).encode())
            else:
                self.report_invalid()
        else:
            self.report_invalid()

        self.transport.close()


class NetworkInterface:
    def __init__(self, config: Config, storage: StorageProvider):
        self.config = config
        self.storage = storage
        self.planner = RoutePlanner(storage)

        config_data = self.config.get_config_value(ConfigKeys.NetworkInterfaceConfig)
        self.address = config_data.get(ConfigDataKeys.NetworkListenAddress)
        self.port = config_data.get(ConfigDataKeys.NetworkListenPort)

    async def serve_loop(self):
        loop = asyncio.get_running_loop()

        server = await loop.create_server(lambda: NetworkProtocol(self), self.address, self.port)

        async with server:
            await server.serve_forever()

    def run(self):
        print("Listening on {}:{}".format(self.address, self.port))
        asyncio.run(self.serve_loop())
