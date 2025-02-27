"""
Copyright © 2023 Austin Berrio
Module: wiki.logger
Description: A class for automating Logger configuration and instantiation.
Usage:

class WikiBase:
    def __init__(self, verbose):
        self.logger = AutoLogger(self.__class__.__name__, verbose)
"""

import logging
import sys


class AutoLogger:
    def __call__(self, cls_name: str, verbose: bool):
        """
        Initialize a Logger instance.

        :param cls_name: The name of the class that inherits from Logger.
        :param verbose: A boolean indicating whether to enable verbose logging.
        """
        _level = logging.DEBUG if verbose else logging.INFO
        _format = "%(levelname)s:%(filename)s:%(lineno)d: %(message)s"
        _logger = logging.getLogger(cls_name)

        # Check if the logger has handlers to avoid adding duplicates
        if not _logger.hasHandlers():
            handler = logging.StreamHandler(stream=sys.stdout)
            formatter = logging.Formatter(_format)
            handler.setFormatter(formatter)
            _logger.addHandler(handler)
            _logger.setLevel(_level)

        return _logger
