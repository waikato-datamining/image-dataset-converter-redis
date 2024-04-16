import argparse

from wai.logging import LOGGING_WARNING

from idc.api import make_list
from ._redis_writer import AbstractRedisStreamWriter


class AbstractRedisBroadcaster(AbstractRedisStreamWriter):
    """
    Ancestor for redis-based broadcasters.
    """

    def __init__(self, redis_host: str = None, redis_port: int = None, redis_db: int = None,
                 channel_out: str = None, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param redis_host: the redis host to use
        :type redis_host: str
        :param redis_port: the port to use
        :type redis_port: int
        :param redis_db: the database to use
        :type redis_db: int
        :param channel_out: the channel to receive the data on
        :type channel_out: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(redis_host=redis_host, redis_port=redis_port, redis_db=redis_db,
                         logger_name=logger_name, logging_level=logging_level)
        self.channel_out = channel_out

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--channel_out", type=str, help="The Redis channel to broadcast the data on.", default=self._default_channel_out(), required=False)
        return parser

    def _default_channel_out(self):
        """
        Returns the default channel for the outgoing data.

        :return: the default channel
        :rtype: str
        """
        return "data_out"

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.channel_out = ns.channel_out

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.channel_out is None:
            self.channel_out = self._default_channel_out()
        self._redis_session.channel_out = self.channel_out

    def _process_data(self, data):
        """
        For processing the incoming data.

        :param data: the incoming data
        :return: the generated data to broadcast
        """
        raise NotImplementedError()

    def write_stream(self, data):
        """
        Saves the data one by one.

        :param data: the data to write (single record or iterable of records)
        """
        for item in make_list(data):
            self.logger().info("Broadcasting on %s: %s" % (self._redis_session.channel_out, item.image_name))
            payload = self._process_data(item)
            self._redis_session.connection.publish(self._redis_session.channel_out, payload)
