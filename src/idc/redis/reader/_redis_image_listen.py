import argparse
import io
from typing import List

from PIL import Image
from wai.logging import LOGGING_WARNING

from idc.api import DATATYPES, data_type_to_class, ImageData
from ._redis_listener import AbstractRedisListener


class RedisImageReader(AbstractRedisListener):

    def __init__(self, redis_host: str = None, redis_port: int = None, redis_db: int = None,
                 channel_in: str = None, timeout: float = None, timeout_action: str = None,
                 sleep_time: float = None, data_type: str = None, prefix: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param redis_host: the redis host to use
        :type redis_host: str
        :param redis_port: the port to use
        :type redis_port: int
        :param redis_db: the database to use
        :type redis_db: int
        :param channel_in: the channel to receive the data on
        :type channel_in: str
        :param timeout: the time in seconds to wait for data
        :type timeout: float
        :param timeout_action: the action to take when a timeout happens
        :type timeout_action: str
        :param sleep_time: the time in seconds between polls
        :type sleep_time: float
        :param prefix: the prefix to use for the image names
        :type prefix: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(redis_host=redis_host, redis_port=redis_port, redis_db=redis_db,
                         channel_in=channel_in, timeout=timeout, timeout_action=timeout_action,
                         sleep_time=sleep_time, logger_name=logger_name, logging_level=logging_level)
        self.data_type = data_type
        self.prefix = prefix
        self._output_cls = None
        self._counter = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "redis-image-listen"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Listens for images being broadcast and forwards them as the specified data type."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-T", "--data_type", choices=DATATYPES, type=str, default=None, help="The type of data to forward", required=True)
        parser.add_argument("-P", "--prefix", type=str, default=None, help="The prefix to use for the images", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.data_type = ns.data_type
        self.prefix = ns.prefix

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        if self.data_type is None:
            return [ImageData]
        else:
            return [data_type_to_class(self.data_type)]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.data_type is None:
            raise Exception("No data type defined!")
        if self.prefix is None:
            self.prefix = ""
        self._output_cls = data_type_to_class(self.data_type)
        self._counter = 0

    def _process_data(self, data):
        """
        For processing the received data.

        :param data: the received data
        :return: the generated output data
        """
        self._counter += 1

        img_io = io.BytesIO(data)
        img = Image.open(img_io)

        image_name = self.prefix
        if len(image_name) > 0:
            image_name += "-"
        image_name += str(self._counter) + "." + img.format.lower().replace("jpeg", "jpg")

        return self._output_cls(image_name=image_name, image=img, image_format=img.format, data=img_io.getvalue())
