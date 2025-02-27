"""
Module: wiki.params
Description: A class for storing parameters related to the wiki conversion process.
"""

import dataclasses
import pathlib
from typing import Literal


# NOTE: Managing the input source files and separating them from the preprocessed text
# files seems to be the most complicated aspect of all of this at the moment.
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

    # This is the repository root path
    @property
    def REPO_PATH(self) -> pathlib.Path:
        return pathlib.Path(self.repo)

    # This represents the original source directory
    @property
    def VERSION_PATH(self) -> list[pathlib.Path]:
        # Dynamically generate paths based on version
        prefix = f"SDL{self.version}"
        submodules = ["", "_image", "_mixer", "_net", "_ttf"]
        return [self.REPO_PATH / f"{prefix}{sub}" for sub in submodules]

    # This is the current working directory
    @property
    def ROOT_PATH(self) -> pathlib.Path:
        return pathlib.Path(self.root)

    # This represents the target destination directory
    @property
    def TEXT_ROOT_DIR(self) -> pathlib.Path:
        return self._ensure_directory(self.ROOT_PATH / "text")

    # This represents the processed target directory
    @property
    def TEXT_OUTPUT_DIR(self) -> pathlib.Path:
        """
        Directory where processed files are saved to preserve originals.
        """
        return self._ensure_directory(self.params.TEXT_ROOT_DIR / "processed")

    # This represents the processed source directory
    @property
    def TEXT_INPUT_DIR(self) -> list[pathlib.Path]:
        # This is used as input to produce the output TEXT file
        prefix = f"SDL{self.params.version}"
        submodules = ["", "_image", "_mixer", "_net", "_ttf"]
        return [self.OUTPUT_DIR / f"{prefix}{sub}" for sub in submodules]

    # This is the product of the concatenated processed source directory
    @property
    def TEXT_FILE(self) -> pathlib.Path:
        # This is used to produce a concatenated TEXT file
        # and is used as input to produce the PDF file
        return self.params.TEXT_ROOT_DIR / f"SDL-Wiki-v{self.params.version}.md"

    # This is the target output path for the PDF file. The TEXT_FILE is a prerequisite
    # since it is used as input to generate the output PDF file using pandoc.
    @property
    def PDF_PATH(self) -> pathlib.Path:
        return self._ensure_directory(self.ROOT_PATH / "pdf")

    # This is the target output path for all MAN pages. The TEXT_INPUT_DIR is a
    # prerequisite since each preprocessed markdown file is used as input to generate
    # each output manual page using pandoc.
    @property
    def MAN_PATH(self) -> pathlib.Path:
        return self._ensure_directory(self.ROOT_PATH / "man")

    def _ensure_directory(self, path: pathlib.Path) -> pathlib.Path:
        """Helper to create directory if it doesn't exist."""
        path.mkdir(parents=True, exist_ok=True)
        return path
