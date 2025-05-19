import argparse
import io
import numpy as np
from typing import List

from PIL import Image
from wai.logging import LOGGING_WARNING

from idc.api import DepthData
from ._redis_pubsub_filter import AbstractRedisPubSubFilter

FORMAT_GRAYSCALE = "grayscale"
FORMAT_GRAYSCALE_DEPTH = "grayscale-depth"
FORMAT_NUMPY = "numpy"
FORMATS = [
    FORMAT_GRAYSCALE,
    FORMAT_GRAYSCALE_DEPTH,
    FORMAT_NUMPY,
]


class DepthRedisPredict(AbstractRedisPubSubFilter):
    """
    Makes depth information predictions via Redis backend.
    """

    def __init__(self, redis_host: str = None, redis_port: int = None, redis_db: int = None,
                 channel_out: str = None, channel_in: str = None, timeout: float = None,
                 timeout_action: str = None, sleep_time: float = None, data_format: str = None,
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
        :param data_format: the format of the predictions
        :type data_format: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(redis_host=redis_host, redis_port=redis_port, redis_db=redis_db,
                         channel_out=channel_out, channel_in=channel_in, timeout=timeout,
                         timeout_action=timeout_action, sleep_time=sleep_time,
                         logger_name=logger_name, logging_level=logging_level)
        self.data_format = data_format

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "redis-predict-dp"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Makes depth information predictions via Redis backend."

    def _default_channel_out(self):
        """
        Returns the default channel for broadcasting the filtered data.

        :return: the default channel
        :rtype: str
        """
        return "images"

    def _default_channel_in(self):
        """
        Returns the default channel for the incoming data.

        :return: the default channel
        :rtype: str
        """
        return "predictions"

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [DepthData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [DepthData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("--data_format", choices=FORMATS, help="The data format of the predictions.", default=FORMAT_GRAYSCALE, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.data_format = ns.data_format

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.data_format is None:
            self.data_format = FORMAT_GRAYSCALE

    def _fix_size(self, img, width, height):
        """
        Fixes the size of the received image, if necessary.

        :param img: the to resize
        :type img: Image.Image
        :param width: the required width
        :type width: int
        :param height: the required height
        :type height: int
        :return: the (potentially) resized image
        :rtype: Image.Image
        """
        if (img.width == width) and (img.height == height):
            return img
        else:
            return img.resize((width, height), Image.Resampling.BILINEAR)

    def _process_data(self, item: DepthData, data):
        """
        For processing the received data.

        :param item: the image data that was sent via redis
        :param data: the received data
        :return: the generated output data
        """
        w = item.image_width
        h = item.image_height

        # convert received data
        if self.data_format == FORMAT_GRAYSCALE:
            annotations = self._fix_size(Image.open(io.BytesIO(data)), w, h)
        elif self.data_format == FORMAT_GRAYSCALE_DEPTH:
            annotations = self._fix_size(Image.open(io.BytesIO(data)), w, h)
        elif self.data_format == FORMAT_NUMPY:
            annotations = np.load(io.BytesIO(data))
        else:
            raise Exception("Unsupported format: %s" % self.data_format)

        return DepthData(source=item.source, data=item.data, annotation=annotations,
                         metadata=item.get_metadata())
