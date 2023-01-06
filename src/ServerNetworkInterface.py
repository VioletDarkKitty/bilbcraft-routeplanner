import asyncio
import json
import re
from json import JSONDecodeError

from src.Config import Config, ConfigKeys, ConfigDataKeys
from src.Location import Position
from src.RoutePlanner import RoutePlanner, RouteTimeoutException
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

                timeout_ms = json_data["timeout"] if "timeout" in json_data.keys() else None
                try:
                    route = self.interface.planner.plan_route(pos1, pos2, timeout_ms)
                    data = []
                    for entry in route.get_entries():
                        data.append(entry)
                    self.transport.write(json.dumps(data).encode())
                except RouteTimeoutException:
                    self.transport.write(json.dumps({
                        "error": "timeout"
                    }).encode())
            else:
                self.report_invalid()
        else:
            self.report_invalid()

        self.transport.close()


class ServerNetworkInterface:
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


class ClientNetworkProtocol(asyncio.Protocol):
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))
        print(self._route_json_to_list(json.loads(data.decode())))

    @staticmethod
    def _location_formatter(data):
        if data["location"] is None:
            return data["position"]
        return "{} {}".format(data["location"]["label"], data["location"]["position"])

    @staticmethod
    def _connection_formatter(data):
        return "{}, {}".format(data["label"], data["description"])

    def _route_json_to_list(self, data):
        formatted = []
        for route in data:
            if route["type"] == "board_train":
                formatted.append("Board the {}".format(self._connection_formatter(route["from"]["connection"])))
            elif route["type"] == "leave_train":
                formatted.append(
                    "Travel {} stops to {} and leave the train".format(route["to"]["num_stops"],
                                                                       self._location_formatter(route["to"])))
            elif route["type"] == "change_train":
                formatted.append("Travel {} stops and change trains at {} and take the {}".format(
                    route["to"]["num_stops"],
                    self._location_formatter(route["to"]),
                    self._connection_formatter(route["to"]["connection"])
                ))
            elif route["type"] in ["enter_street", "change_street", "walk"]:
                formatted.append("Walk {} blocks from {} to {}".format(
                    route["distance"],
                    self._location_formatter(route["from"]),
                    self._location_formatter(route["to"])
                ))

        return '\n'.join(formatted)

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)


class ClientNetworkInterface:
    def __init__(self, config: Config, storage: StorageProvider):
        self.config = config
        self.storage = storage

        self.address = "127.0.0.1"
        self.port = 28_581

        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

        self.tuple_re = re.compile(r"(?:\()?(-?[0-9]+),(?: *)(-?[0-9]+)(?:\))?")

    async def client_connection(self):
        loop = asyncio.get_running_loop()

        on_con_lost = loop.create_future()
        data = {
            "type": "route",
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "timeout": 100_000
        }
        message = json.dumps(data)

        transport, protocol = await loop.create_connection(lambda: ClientNetworkProtocol(message, on_con_lost),
                                                           self.address, self.port)

        try:
            await on_con_lost
        finally:
            transport.close()

    def get_position(self, message, default=None):
        match = None
        while match is None:
            input_data = input(message.format("(default {})".format(default)))
            if input_data == "" and default is not None:
                print("(default)")
                return default
            match = self.tuple_re.match(input_data)
        return int(match.group(1)), int(match.group(2))

    def run(self):
        start_pos = self.get_position("Start position x,y {}: ", default=(87, -220))
        self.x1 = start_pos[0]
        self.y1 = start_pos[1]
        end_pos = self.get_position("End position x,y {}: ", default=(12177, -256))
        self.x2 = end_pos[0]
        self.y2 = end_pos[1]

        asyncio.run(self.client_connection())
