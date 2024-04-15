import argparse
from dataclasses import dataclass
from datetime import datetime
from time import sleep

import redis
from seppl.io import Filter
from wai.logging import LOGGING_WARNING

from idc.api import flatten_list, make_list


@dataclass
class RedisFilterSession:
    connection: redis.Redis = None
    channel_out: str = "images"
    channel_in: str = "predictions"
    timeout: float = 5.0
    data = None
    pubsub = None
    pubsub_thread = None


TIMEOUT_ACTION_DROP = "drop"
TIMEOUT_ACTION_INPUT = "input"
TIMEOUT_ACTIONS = [
    TIMEOUT_ACTION_DROP,
    TIMEOUT_ACTION_INPUT,
]


class AbstractRedisFilter(Filter):
    """
    Ancestor for redis-based filters.
    """

    def __init__(self, redis_host: str = None, redis_port: int = None, redis_db: int = None,
                 channel_out: str = None, channel_in: str = None, timeout: float = None,
                 timeout_action: str = None, sleep_time: float = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param redis_host: the redis host to use
        :type redis_host: str
        :param redis_port: the port to use
        :type redis_port: int
        :param redis_db: the database to use
        :type redis_db: int
        :param channel_out: the channel to send the images to
        :type channel_out: str
        :param channel_in: the channel to receive the predictions on
        :type channel_in: str
        :param timeout: the time in seconds to wait for predictions
        :type timeout: float
        :param timeout_action: the action to take when a timeout happens
        :type timeout_action: str
        :param sleep_time: the time in seconds between polls
        :type sleep_time: float
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.channel_out = channel_out
        self.channel_in = channel_in
        self.timeout = timeout
        self.timeout_action = timeout_action
        self.sleep_time = sleep_time
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
        parser.add_argument("-o", "--channel_out", type=str, help="The Redis channel to send the data out.", default=self._default_channel_out(), required=False)
        parser.add_argument("-i", "--channel_in", type=str, help="The Redis channel to receive the data on.", default=self._default_channel_in(), required=False)
        parser.add_argument("-t", "--timeout", type=float, help="The timeout in seconds to wait for a data to arrive.", default=5.0, required=False)
        parser.add_argument("-a", "--timeout_action", choices=TIMEOUT_ACTIONS, help="The action to take when a timeout occurs.", default=TIMEOUT_ACTION_DROP, required=False)
        parser.add_argument("-s", "--sleep_time", type=float, help="The time in seconds between polls.", default=0.01, required=False)
        return parser

    def _default_channel_out(self):
        """
        Returns the default channel for broadcasting the filtered data.

        :return: the default channel
        :rtype: str
        """
        return "data_out"

    def _default_channel_in(self):
        """
        Returns the default channel for the incoming data.

        :return: the default channel
        :rtype: str
        """
        return "data_in"

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
        self.channel_out = ns.channel_out
        self.channel_in = ns.channel_in
        self.timeout = ns.timeout
        self.timeout_action = ns.timeout_action
        self.sleep_time = ns.sleep_time

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
        if self.channel_out is None:
            self.channel_out = "images"
        if self.channel_in is None:
            self.channel_in = "predictions"
        if self.timeout is None:
            self.timeout = 5.0
        if self.timeout_action is None:
            self.timeout_action = TIMEOUT_ACTION_DROP
        if self.sleep_time is None:
            self.sleep_time = 0.01
        self._redis_session = RedisFilterSession()
        self._redis_session.connection = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)
        self._redis_session.channel_out = self.channel_out
        self._redis_session.channel_in = self.channel_in
        self._redis_session.timeout = self.timeout
        self._redis_session.data = None

    def _process_data(self, item, data):
        """
        For processing the received data.

        :param item: the image data that was sent via redis
        :param data: the received data
        :return: the generated output data
        """
        raise NotImplementedError()

    def _do_process(self, data):
        """
        Processes the data record(s).

        :param data: the record(s) to process
        :return: the potentially updated record(s)
        """
        result = []

        for item in make_list(data):

            def anon_handler(message):
                d = message['data']
                self._redis_session.data = d
                self._redis_session.pubsub_thread.stop()
                self._redis_session.pubsub.close()
                self._redis_session.pubsub_thread = None
                self._redis_session.pubsub = None

            self._redis_session.pubsub = self._redis_session.connection.pubsub()
            self._redis_session.pubsub.psubscribe(**{self._redis_session.channel_in: anon_handler})
            self._redis_session.pubsub_thread = self._redis_session.pubsub.run_in_thread(sleep_time=self.sleep_time)
            self._redis_session.connection.publish(self._redis_session.channel_out, item.image_bytes)

            # wait for data to show up
            start = datetime.now()
            no_data = False
            while self._redis_session.pubsub is not None:
                sleep(self.sleep_time)
                end = datetime.now()
                if self._redis_session.timeout > 0:
                    if (end - start).total_seconds() >= self._redis_session.timeout:
                        self.logger().info("Timeout reached!")
                        no_data = True
                        self._redis_session.pubsub_thread.stop()
                        self._redis_session.pubsub_thread = None
                        self._redis_session.pubsub = None
                        break

            if no_data:
                if self.timeout_action == TIMEOUT_ACTION_DROP:
                    continue
                elif self.timeout_action == TIMEOUT_ACTION_INPUT:
                    result.append(item)
                    continue
                else:
                    raise Exception("Unhandled timeout action: %s" % self.timeout_action)
            else:
                end = datetime.now()
                self.logger().info("Round trip time: %f sec" % (end - start).total_seconds())

            # process data
            item_new = self._process_data(item, self._redis_session.data)

            if item_new is not None:
                result.append(item_new)

        return flatten_list(result)
