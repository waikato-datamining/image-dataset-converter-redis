import argparse
import io
from typing import List

from PIL import Image
from wai.logging import LOGGING_WARNING

from idc.api import ImageSegmentationData, from_bluechannel, from_grayscale, from_indexedpng
from idc.redis_pred.filter._redis_filter import AbstractRedisFilter

FORMAT_INDEXEDPNG = "indexedpng"
FORMAT_BLUECHANNEL = "bluechannel"
FORMAT_GRAYSCALE = "grayscale"
FORMATS = [
    FORMAT_INDEXEDPNG,
    FORMAT_BLUECHANNEL,
    FORMAT_GRAYSCALE,
]


class ImageSegmentationRedisPredict(AbstractRedisFilter):
    """
    Ancestor for filters that perform predictions via Redis.
    """

    def __init__(self, redis_host: str = None, redis_port: int = None, redis_db: int = None,
                 channel_out: str = None, channel_in: str = None, timeout: float = None,
                 sleep_time: float = None, image_format: str = None,
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
        :param sleep_time: the time in seconds between polls
        :type sleep_time: float
        :param image_format: the format of the predictions
        :type image_format: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(redis_host=redis_host, redis_port=redis_port, redis_db=redis_db,
                         channel_out=channel_out, channel_in=channel_in, timeout=timeout,
                         sleep_time=sleep_time, logger_name=logger_name, logging_level=logging_level)
        self.image_format = image_format

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "redis-predict-is"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Makes image segmentation predictions via Redis backend."

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ImageSegmentationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [ImageSegmentationData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("--image_format", choices=FORMATS, help="The image format of the predictions.", default=FORMAT_INDEXEDPNG, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.image_format = ns.image_format

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.image_format is None:
            self.image_format = FORMAT_INDEXEDPNG

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

    def _process_data(self, item: ImageSegmentationData, data):
        """
        For processing the received data.

        :param item: the image data that was sent via redis
        :param data: the received data
        :return: the generated output data
        """
        w = item.image_width
        h = item.image_height

        label_mapping = dict()
        for i, label in enumerate(item.annotation.labels):
            label_mapping[i] = label

        # convert received image to indices
        image = self._fix_size(Image.open(io.BytesIO(data)), w, h)
        if self.image_format == FORMAT_INDEXEDPNG:
            annotations = from_indexedpng(image, item.annotation.labels, label_mapping, self.logger())
        elif self.image_format == FORMAT_BLUECHANNEL:
            annotations = from_bluechannel(image, item.annotation.labels, label_mapping, self.logger())
        elif self.image_format == FORMAT_GRAYSCALE:
            annotations = from_grayscale(image, item.annotation.labels, label_mapping, self.logger())
        else:
            raise Exception("Unsupported image format: %s" % self.image_format)

        return ImageSegmentationData(source=item.source, data=item.data, annotation=annotations,
                                     metadata=item.get_metadata())
