"""
Module: wiki.params
Description: A class for storing parameters related to the wiki conversion process.
"""

import dataclasses
import os
import pathlib
from typing import Literal


@dataclasses.dataclass
class WikiParameters:
    repo: str  # The repository path to clone, sync, or reference
    root: str  # The parent path for the current working directory
    conversion_type: Literal["text", "pdf", "man"]  # Type of conversion process
    version: Literal["2", "3"]  # Version of the docs, e.g. 2 or 3
    verbose: bool  # Enable debug info

    def __post_init__(self):
        # Default to upstream source
        if self.repo == ".":
            self.repo = "libsdl-org/sdlwiki"

        # Default to local path if specified
        if self.root == ".":
            self.root = os.getcwd()

        # Validate conversion type
        if self.conversion_type not in {"text", "pdf", "man"}:
            raise ValueError(f"Invalid conversion_type: {self.conversion_type}")

        # Validate version
        if self.version not in {"2", "3"}:
            raise ValueError(f"Invalid version: {self.version}")

    @property
    def REPO_PATH(self) -> pathlib.Path:
        return pathlib.Path(self.params.repo)

    @property
    def VERSION_PATH(self) -> list[pathlib.Path]:
        version_map = {
            "2": ["SDL2", "SDL2_image", "SDL2_mixer", "SDL2_net", "SDL2_ttf"],
            "3": ["SDL3", "SDL3_image", "SDL3_mixer", "SDL3_net", "SDL3_ttf"],
        }
        return [self.REPO_PATH / v for v in version_map[self.params.version]]

    @property
    def ROOT_PATH(self) -> pathlib.Path:
        return pathlib.Path(self._root)

    @property
    def TEXT_PATH(self) -> pathlib.Path:
        text_dir = self.ROOT_PATH / "text"
        text_dir.mkdir(parents=True, exist_ok=True)
        return text_dir

    @property
    def PDF_PATH(self) -> pathlib.Path:
        pdf_dir = self.ROOT_PATH / "pdf"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        return pdf_dir

    @property
    def MAN_PATH(self) -> pathlib.Path:
        man_dir = self.ROOT_PATH / "man"
        man_dir.mkdir(parents=True, exist_ok=True)
        return man_dir
