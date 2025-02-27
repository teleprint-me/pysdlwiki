"""
Module: wiki.params
Description: A class for storing parameters related to the wiki conversion process.
"""

import dataclasses
import os


@dataclasses.dataclass
class WikiParameters:
    repo: str  # The repository path to clone, sync, or reference
    root: str  # The parent path for the current working directory
    _type: str  # The type of conversion process, e.g. text, pdf, man
    version: str  # The version of the docs, e.g. 2 or 3
    verbose: bool  # Enable debug info

    def __post_init__(self):
        # Default to upstream source
        if self.repo == ".":
            self.repo = "libsdl-org/sdlwiki"

        # Default to local path if specified
        if self.root == ".":
            self.root = os.getcwd()
