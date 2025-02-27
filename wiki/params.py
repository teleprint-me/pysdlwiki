"""
Module: wiki.params
Description: A class for storing parameters related to the wiki conversion process.
"""

import dataclasses
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
            self.root = pathlib.Path.cwd()

        # Validate conversion type
        if self.conversion_type not in {"text", "pdf", "man"}:
            raise ValueError(f"Invalid conversion_type: {self.conversion_type}")

        # Validate version
        if self.version not in {"2", "3"}:
            raise ValueError(f"Invalid version: {self.version}")

    @property
    def REPO_PATH(self) -> pathlib.Path:
        return pathlib.Path(self.repo)

    @property
    def VERSION_PATH(self) -> list[pathlib.Path]:
        # Dynamically generate paths based on version
        prefix = f"SDL{self.version}"
        submodules = ["", "_image", "_mixer", "_net", "_ttf"]
        return [self.REPO_PATH / f"{prefix}{sub}" for sub in submodules]

    @property
    def ROOT_PATH(self) -> pathlib.Path:
        return pathlib.Path(self.root)

    @property
    def TEXT_PATH(self) -> pathlib.Path:
        return self._ensure_directory(self.ROOT_PATH / "text")

    @property
    def PDF_PATH(self) -> pathlib.Path:
        return self._ensure_directory(self.ROOT_PATH / "pdf")

    @property
    def MAN_PATH(self) -> pathlib.Path:
        return self._ensure_directory(self.ROOT_PATH / "man")

    def _ensure_directory(self, path: pathlib.Path) -> pathlib.Path:
        """Helper to create directory if it doesn't exist."""
        path.mkdir(parents=True, exist_ok=True)
        return path
