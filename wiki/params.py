"""
Copyright © 2023 Austin Berrio
Module: wiki.params
Description:
    A class for managing parameters and file paths related to the SDL Wiki conversion process.
    Centralized configuration and path management for the SDL Wiki conversion pipeline.

Path Flow:
    - Input Source: REPO_PATH/<version_dir>/<file>
    - Intermediate Representation (IR): OUTPUT_DIR/text/<ir_dir>/<version_dir>/<ir_file>
    - Final Outputs:
        - TEXT: OUTPUT_DIR/text/SDL-Wiki-v{version}.md
        - PDF: OUTPUT_DIR/pdf/SDL-Wiki-v{version}.pdf
        - MAN Pages: OUTPUT_DIR/man/<man_file>

Design Rationale:
    - REPO_PATH is the original source input.
    - OUTPUT_DIR is the final output destination, organized by conversion type.
    - IR_DIR is both the target output and the source input for further processing.
    - TEXT_OUTPUT_FILE is the final concatenated Markdown file.
    - PDF_OUTPUT_FILE is the final output PDF file.
"""

import dataclasses
import pathlib
from typing import Any, Dict, List, Literal


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

    # ========== Core Directory Structure ========== #

    @property
    def ROOT_PATH(self) -> pathlib.Path:
        """The current working directory for the conversion process."""
        return pathlib.Path(self.root)

    @property
    def REPO_PATH(self) -> pathlib.Path:
        """The root path of the cloned SDL Wiki repository."""
        return pathlib.Path(self.repo)

    @property
    def VERSION_DIRS(self) -> List[pathlib.Path]:
        """
        The original source directories for the selected version.
        These represent the unprocessed input directories.
        """
        prefix = f"SDL{self.version}"
        submodules = ["", "_image", "_mixer", "_net", "_ttf"]
        return [self.REPO_PATH / f"{prefix}{sub}" for sub in submodules]

    # ========== Output Directories and Files ========== #

    @property
    def OUTPUT_DIR(self) -> pathlib.Path:
        """Root directory for all final output files."""
        return self._ensure_directory(self.ROOT_PATH / "output")

    @property
    def TEXT_OUTPUT_DIR(self) -> pathlib.Path:
        """Directory for storing concatenated Markdown files."""
        return self._ensure_directory(self.OUTPUT_DIR / "text")

    @property
    def PDF_OUTPUT_DIR(self) -> pathlib.Path:
        """Directory for storing generated PDF files."""
        return self._ensure_directory(self.OUTPUT_DIR / "pdf")

    @property
    def MAN_OUTPUT_DIR(self) -> pathlib.Path:
        """Directory for storing generated MAN pages."""
        return self._ensure_directory(self.OUTPUT_DIR / "man")

    # ========== Intermediate Representation (IR) ========== #

    @property
    def IR_DIR(self) -> pathlib.Path:
        """
        Intermediate Representation (IR) directory for all processed files.
        These are sanitized and normalized Markdown files, ready for further processing.
        """
        return self._ensure_directory(self.TEXT_OUTPUT_DIR / "intermediate")

    @property
    def IR_VERSION_DIRS(self) -> list[pathlib.Path]:
        """
        Directories containing IR files for further processing.
        Mirrors the structure of VERSION_DIRS.
        """
        prefix = f"SDL{self.version}"
        submodules = ["", "_image", "_mixer", "_net", "_ttf"]
        return [self.IR_DIR / f"{prefix}{sub}" for sub in submodules]

    # ========== Final Output Files ========== #

    @property
    def TEXT_OUTPUT_FILE(self) -> pathlib.Path:
        """
        Concatenated Markdown file, used as input for generating PDFs.
        """
        return self.TEXT_OUTPUT_DIR / f"SDL-Wiki-v{self.version}.md"

    @property
    def PDF_OUTPUT_FILE(self) -> pathlib.Path:
        """Final PDF file generated from the concatenated Markdown."""
        return self.PDF_OUTPUT_DIR / f"SDL-Wiki-v{self.version}.pdf"

    # ========== Utilities ========== #

    def _ensure_directory(self, path: pathlib.Path) -> pathlib.Path:
        """Helper to create directory if it doesn't exist."""
        path.mkdir(parents=True, exist_ok=True)
        return path

    def as_dict(self) -> Dict[str, Any]:
        """Returns a dictionary representation of the defined parameters."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
