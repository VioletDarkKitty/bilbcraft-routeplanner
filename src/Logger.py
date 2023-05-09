import datetime
import sqlite3
import typing
from abc import ABC, abstractmethod
from enum import Enum


class LoggerException(Exception):
    pass


class LogLevel(Enum):
    Debug = -2
    Info = -1
    Warning = 0
    Error = 1
    Fatal = 2

    @classmethod
    def from_name(cls, level):
        for vs in LogLevel:
            if vs.name == level:
                return vs
        return None


class LogEntry:
    def __init__(self, entry_id: typing.Optional[int], timestamp: datetime.datetime, log_level: LogLevel, data: str):
        self.entry_id = entry_id
        self.timestamp = timestamp
        self.log_level = log_level
        self.data = data

    @staticmethod
    def create(log_level: LogLevel, data: str):
        return LogEntry(None, datetime.datetime.now(), log_level, data)

    def get_timestamp(self):
        return self.timestamp

    def get_log_level(self):
        return self.log_level.name.format()

    def get_text(self):
        return self.data

    def get_id(self) -> int:
        return self.entry_id


class Logger(ABC):
    def __init__(self):
        pass

    @staticmethod
    def create(logger_type, data):
        types = {
            "db": DbLogger
        }
        if logger_type in types.keys():
            return types[logger_type](**data)
        else:
            raise LoggerException("Unknown logger type {}".format(logger_type))

    @abstractmethod
    def add_entry(self, entry: LogEntry):
        pass

    @abstractmethod
    def get_next_entry(self, entry_id) -> LogEntry:
        pass

    @abstractmethod
    def get_prev_entry(self, entry_id):
        pass

    @abstractmethod
    def get_entry_range(self, begin_id, end_id):
        pass

    @abstractmethod
    def format_log_entry(self, entry: LogEntry) -> str:
        pass


class DbLogger(Logger):
    def __init__(self, db_path):
        super().__init__()
        self.db_connection = sqlite3.connect(db_path)
        self.cursor = self.db_connection.cursor()

        self.version = 1
        self._init_tables()

    def _init_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS config(key TEXT PRIMARY KEY, value TEXT)")
        self.cursor.execute("INSERT OR IGNORE INTO config(key, value) VALUES(?, ?) ", ("version", self.version,))
        self.cursor.execute("CREATE TABLE IF NOT EXISTS log_entries(id INTEGER PRIMARY KEY ASC, date INTEGER, "
                            "level INTEGER, text TEXT)")
        self.db_connection.commit()

    def add_entry(self, entry: LogEntry):
        self.cursor.execute("INSERT INTO log_entries(date, level, text) VALUES(?, ?, ?)",
                            (entry.get_timestamp(), entry.get_log_level(), entry.get_text(),))
        self.db_connection.commit()
        print(self.format_log_entry(entry))

    def get_next_entry(self, entry_id):
        if entry_id is None:
            res = self.cursor.execute("SELECT id, date, level, text FROM log_entries ORDER BY id LIMIT 1")
        else:
            res = self.cursor.execute("SELECT id, date, level, text FROM log_entries WHERE id > ? ORDER BY id LIMIT 1",
                                      (entry_id, ))
        entry_data = res.fetchone()
        if entry_data is None:
            return None

        return LogEntry(entry_data[0], entry_data[1], LogLevel.from_name(entry_data[2]), entry_data[3])

    def get_prev_entry(self, entry_id):
        pass

    def get_entry_range(self, begin_id, end_id):
        pass

    def format_log_entry(self, entry: LogEntry) -> str:
        return "[{}] ({}): {}".format(entry.get_timestamp(), entry.get_log_level(), entry.get_text())
