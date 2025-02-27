# file: wiki/logger.py (1-21)
"""
Copyright © 2023 Austin Berrio
Module: wiki.logger
Description: A simple parent class for child classes to inherit from.
Usage:
    class WikiBase(Logger):
        def __init__(self, repo_path: str, type: str, version: int, verbose: bool):
            super().__init__(self.__class__.__name__, verbose)
"""

import logging


class WikiLogger:
    def __init__(self, cls_name: str, verbose: bool):
        """
        Initialize a Logger instance.

        :param cls_name: The name of the class that inherits from Logger.
        :param verbose: A boolean indicating whether to enable verbose logging.
        """
        self.level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=self.level,
            format="%(levelname)s:%(filename)s:%(lineno)d: %(message)s",
        )
        self.logger = logging.getLogger(cls_name)
