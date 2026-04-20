import argparse
import json
import logging
from typing import List

from wai.logging import LOGGING_WARNING

from kasperl.redis.filter import AbstractRedisPubSubFilter
from idc.api import ImageClassificationData


class ImageClassificationRedisPredict(AbstractRedisPubSubFilter):
    """
    Makes image classification predictions via Redis backend.
    """

    def __init__(self, redis_host: str = None, redis_port: int = None, redis_db: int = None,
                 channel_out: str = None, channel_in: str = None, timeout: float = None,
                 timeout_action: str = None, sleep_time: float = None, key_raw: str = None,
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
        :param key_raw: the key in the meta-data to store the full prediction result under
        :type key_raw: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(redis_host=redis_host, redis_port=redis_port, redis_db=redis_db,
                         channel_out=channel_out, channel_in=channel_in, timeout=timeout,
                         timeout_action=timeout_action, sleep_time=sleep_time,
                         logger_name=logger_name, logging_level=logging_level)
        self.key_raw = key_raw

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "redis-predict-ic"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Makes image classification predictions via Redis backend."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("--key_raw", metavar="KEY", type=str, default=None, help="The key in the meta-data to store the raw prediction result under.")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.key_raw = ns.key_raw

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
        return [ImageClassificationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [ImageClassificationData]

    def _process_data(self, item: ImageClassificationData, data):
        """
        For processing the received data.

        :param item: the image data that was sent via redis
        :param data: the received data
        :return: the generated output data
        """
        if self.logger().isEnabledFor(logging.DEBUG):
            self.logger().debug(data)

        # convert to wai.annotations annotations
        preds = json.loads(data)
        max_key = None
        max_value = 0.0
        for k in preds:
            if preds[k] > max_value:
                max_key = k
                max_value = preds[k]

        meta = item.get_metadata()

        # store raw result?
        if self.key_raw is not None:
            if meta is None:
                meta = dict()
            meta[self.key_raw] = str(data)

        if self.logger().isEnabledFor(logging.DEBUG):
            self.logger().debug("max_value=%f and max_key=%s" % (max_value, max_key))

        return ImageClassificationData(source=item.source, image_name=item.image_name, data=item.data,
                                       annotation=max_key, metadata=meta)
