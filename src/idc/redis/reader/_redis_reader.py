import argparse

import redis
from wai.logging import LOGGING_WARNING

from idc.api import Reader
from idc.redis.core import RedisSession


class AbstractRedisReader(Reader):
    """
    Ancestor for redis-based readers.
    """

    def __init__(self, redis_host: str = None, redis_port: int = None, redis_db: int = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param redis_host: the redis host to use
        :type redis_host: str
        :param redis_port: the port to use
        :type redis_port: int
        :param redis_db: the database to use
        :type redis_db: int
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self._redis_session = None

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-H", "--redis_host", type=str, help="The Redis server to connect to.", default="localhost", required=False)
        parser.add_argument("-p", "--redis_port", type=int, help="The port the Redis server is running on.", default=6379, required=False)
        parser.add_argument("-d", "--redis_db", type=int, help="The database to use.", default=0, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.redis_host = ns.redis_host
        self.redis_port = ns.redis_port
        self.redis_db = ns.redis_db

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.redis_host is None:
            self.redis_host = "localhost"
        if self.redis_port is None:
            self.redis_port = 6379
        if self.redis_db is None:
            self.redis_db = 0
        self._redis_session = RedisSession()
        self._redis_session.connection = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)
