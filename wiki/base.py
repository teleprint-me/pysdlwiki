"""
Copyright © 2023 Austin Berrio
Module: wiki.base
Description: Base class for converting SDL Wiki from HTML to a selected output format.
"""

import os
import pathlib
import platform
import shutil
import subprocess
from typing import IO, Any, List

from wiki.logger import Logger


class WikiBase(Logger):
    def __init__(self, repo_path: str, _type: str, version: int, verbose: bool):
        super().__init__(self.__class__.__name__, verbose)

        # Use the local path if specified
        if repo_path == ".":
            repo_path = os.getcwd()  # Normalize the local path

        # Otherwise, target the repo defined by user
        self._repo_path = repo_path
        self._type = _type
        self._version = str(version)
        self._verbose = verbose

    @property
    def REPO_PATH(self) -> pathlib.Path:
        return pathlib.Path(self._repo_path)

    @property
    def VERSION_PATH(self) -> List[pathlib.Path]:
        version_map = {
            "2": ["SDL2", "SDL2_image", "SDL2_mixer", "SDL2_net", "SDL2_ttf"],
            "3": ["SDL3", "SDL3_image", "SDL3_mixer", "SDL3_net", "SDL3_ttf"],
        }
        return [self.REPO_PATH / v for v in version_map[self._version]]

    @property
    def TEXT_PATH(self) -> pathlib.Path:
        text_dir = self.REPO_PATH / "text"
        text_dir.mkdir(parents=True, exist_ok=True)
        return text_dir

    @property
    def PDF_PATH(self) -> pathlib.Path:
        pdf_dir = self.REPO_PATH / "pdf"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        return pdf_dir

    @property
    def MAN_PATH(self) -> pathlib.Path:
        man_dir = self.REPO_PATH / "man"
        man_dir.mkdir(parents=True, exist_ok=True)
        return man_dir

    @property
    def TEXT_FILE(self) -> pathlib.Path:
        return self.TEXT_PATH / f"SDL-Wiki-v{self._version}.md"

    @property
    def PDF_FILE(self) -> pathlib.Path:
        return self.PDF_PATH / f"SDL-Wiki-v{self._version}.pdf"

    def log(self) -> None:
        # OS info
        self.logger.debug(f"OS Name: {os.name}")
        self.logger.debug(f"Platform System: {platform.system()}")
        self.logger.debug(f"Platform Release: {platform.release()}")
        # User parameters
        self.logger.debug(f"Conversion Path: {self._repo_path}")
        self.logger.debug(f"Conversion Type: {self._type}")
        self.logger.debug(f"Conversion Version: {self._version}")
        # Automated parameters
        self.logger.debug(f"Repository Path: {base.REPO_PATH}")
        self.logger.debug(f"Version Paths: {base.VERSION_PATH}")
        self.logger.debug(f"Text Path: {base.TEXT_PATH}")
        self.logger.debug(f"PDF Path: {base.PDF_PATH}")
        self.logger.debug(f"Man Path: {base.MAN_PATH}")

    def test(self) -> None:
        prerequisites = ["html2text", "pandoc", "xelatex", "fmtutil-sys", "gs", "git"]
        self.logger.debug(f"Required Prerequisites: {prerequisites}")
        self.logger.debug("Asserting prerequisite discovery...")
        for requisite in prerequisites:
            if not shutil.which(requisite):
                self.logger.error(f"{requisite} not found. Please install it.")
                exit(1)
        self.logger.debug("Prerequisite discovery completed successfully.")

    def run(
        self, args: List[str], stdout: IO = None
    ) -> subprocess.CompletedProcess[Any]:
        params = {"check": True, "capture_output": True, "text": True}
        if stdout:
            params["stdout"] = stdout

        try:
            return subprocess.run(args, **params)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {e.cmd}")
            self.logger.error(f"Return code: {e.returncode}")
            self.logger.error(f"Output: {e.stdout}")
            self.logger.error(f"Error: {e.stderr}")
            exit(1)


if __name__ == "__main__":
    # Set verbosity to off for now
    # Use text mode
    # Look for v2 related docs
    base = WikiBase(repo_path=".", _type="text", version="2", verbose=True)

    base.log()  # Always log before doing anything else
    base.test()
    result = base.run(["echo", "hello,", " world!"])
    print(result.stdout.strip())
