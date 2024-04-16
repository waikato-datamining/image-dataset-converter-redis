import argparse
from typing import List

from opex import ObjectPredictions
from wai.common.adams.imaging.locateobjects import LocatedObjects, LocatedObject
from wai.common.geometry import Polygon, Point
from wai.logging import LOGGING_WARNING

from idc.api import ObjectDetectionData
from ._redis_pubsub_filter import AbstractRedisPubSubFilter


class ObjectDetectionRedisPredict(AbstractRedisPubSubFilter):
    """
    Ancestor for filters that perform predictions via Redis.
    """

    def __init__(self, redis_host: str = None, redis_port: int = None, redis_db: int = None,
                 channel_out: str = None, channel_in: str = None, timeout: float = None,
                 sleep_time: float = None, timeout_action: str = None,
                 key_label: str = None, key_score: str = None,
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
        :param key_label: the key in the meta-data for the label
        :type key_label: str
        :param key_score: the key in the meta-data for the score
        :type key_score: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(redis_host=redis_host, redis_port=redis_port, redis_db=redis_db,
                         channel_out=channel_out, channel_in=channel_in, timeout=timeout,
                         timeout_action=timeout_action, sleep_time=sleep_time,
                         logger_name=logger_name, logging_level=logging_level)
        self.key_label = key_label
        self.key_score = key_score

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "redis-predict-od"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Makes object detection predictions via Redis backend."

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ObjectDetectionData]

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

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [ObjectDetectionData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("--key_label", type=str, help="The key in the metadata for the storing the label.", default="type", required=False)
        parser.add_argument("--key_score", type=str, help="The key in the metadata for the storing the score.", default="score", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.key_label = ns.key_label
        self.key_score = ns.key_score

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.key_label is None:
            self.key_label = "type"
        if self.key_score is None:
            self.key_score = "score"

    def _process_data(self, item: ObjectDetectionData, data):
        """
        For processing the received data.

        :param item: the image data that was sent via redis
        :param data: the received data
        :return: the generated output data
        """
        oobjects = ObjectPredictions.from_json_string(data)
        lobjects = []
        for oobject in oobjects.objects:
            # bbox
            obbox = oobject.bbox
            x = obbox.left
            y = obbox.top
            w = obbox.right - obbox.left + 1
            h = obbox.bottom - obbox.top + 1

            # polygon
            opoly = oobject.polygon
            lpoints = []
            for opoint in opoly.points:
                lpoints.append(Point(x=opoint[0], y=opoint[1]))
            lpoly = Polygon(*lpoints)

            # metadata
            metadata = dict()
            if hasattr(oobject, "score"):
                metadata[self.key_score] = oobject.score
            metadata[self.key_label] = oobject.label

            # add object
            located_object = LocatedObject(x, y, w, h, **metadata)
            located_object.set_polygon(lpoly)
            lobjects.append(located_object)

        annotations = LocatedObjects(lobjects)

        return ObjectDetectionData(source=item.source, data=item.data, annotation=annotations,
                                   metadata=item.get_metadata())
