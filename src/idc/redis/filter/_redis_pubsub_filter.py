import argparse
from datetime import datetime
from time import sleep

from wai.logging import LOGGING_WARNING

from idc.api import flatten_list, make_list
from ._redis_filter import AbstractRedisFilter

TIMEOUT_ACTION_DROP = "drop"
TIMEOUT_ACTION_INPUT = "input"
TIMEOUT_ACTIONS = [
    TIMEOUT_ACTION_DROP,
    TIMEOUT_ACTION_INPUT,
]


class AbstractRedisPubSubFilter(AbstractRedisFilter):
    """
    Ancestor for redis-based pub-sub filters.
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
        :param channel_in: the channel to receive the data on
        :type channel_in: str
        :param timeout: the time in seconds to wait for data
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
        super().__init__(redis_host=redis_host, redis_port=redis_port, redis_db=redis_db,
                         logger_name=logger_name, logging_level=logging_level)
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
        parser.add_argument("-o", "--channel_out", type=str, help="The Redis channel to send the data out.", default=self._default_channel_out(), required=False)
        parser.add_argument("-i", "--channel_in", type=str, help="The Redis channel to receive the data on.", default=self._default_channel_in(), required=False)
        parser.add_argument("-t", "--timeout", type=float, help="The timeout in seconds to wait for a data to arrive.", default=self._default_timeout(), required=False)
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

    def _default_timeout(self):
        """
        Returns the default timeout to use.

        :return: the default timeout in seconds
        :rtype: float
        """
        return 5.0

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
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
        if self.channel_out is None:
            self.channel_out = self._default_channel_out()
        if self.channel_in is None:
            self.channel_in = self._default_channel_in()
        if self.timeout is None:
            self.timeout = self._default_timeout()
        if self.timeout_action is None:
            self.timeout_action = TIMEOUT_ACTION_DROP
        if self.sleep_time is None:
            self.sleep_time = 0.01
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
