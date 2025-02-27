"""
Copyright © 2023 Austin Berrio
Module: wiki.logger
Description: A class for automating Logger configuration and instantiation.
Usage:

class WikiBase:
    def __init__(self, verbose):
        self.logger = AutoLogger.create(self.__class__.__name__, verbose)

NOTE: I think thread-locking here is overkill, but I'm willing to give it a shot.
It might prove useful down the line and I'd rather have it be available than not.
If it isn't used, it's trivial to remove. So no real loss here.
"""

import logging
import sys
from threading import Lock


class AutoLogger:
    """
    A callable class for automating the creation and configuration of loggers.
    """

    lock = Lock()

    @classmethod
    def create(cls, cls_name: str, verbose: bool) -> logging.Logger:
        """
        Initialize and return a Logger instance.

        :param cls_name: The name of the class that inherits from Logger.
        :param verbose: A boolean indicating whether to enable verbose logging.
        :return: Configured logger instance.
        """
        _level = logging.DEBUG if verbose else logging.INFO
        _format = "%(levelname)s:%(filename)s:%(lineno)d: %(message)s"
        _logger = logging.getLogger(cls_name)

        # Thread-safe check to avoid duplicate handlers
        with cls.lock:
            if _logger.level != _level:
                _logger.setLevel(_level)

            # Check if the logger has handlers to avoid adding duplicates
            if not _logger.hasHandlers():
                handler = logging.StreamHandler(stream=sys.stdout)
                formatter = logging.Formatter(_format)
                handler.setFormatter(formatter)
                _logger.addHandler(handler)

        return _logger
