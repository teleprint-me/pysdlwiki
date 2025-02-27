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
from typing import Any, List

from wiki.logger import WikiLogger


class WikiBase(WikiLogger):
    def __init__(self, repo: str, root: str, _type: str, version: int, verbose: bool):
        super().__init__(self.__class__.__name__, verbose)

        # Use the local path if specified
        if repo == ".":
            repo = "libsdl-org/sdlwiki"

        if root == ".":
            root = os.getcwd()

        # Otherwise, target the repo defined by user
        self._repo = repo  # The repository path to clone, sync, or reference
        self._root = root  # The parent path for the current working directory
        self._type = _type  # The type of conversion process, e.g. text, pdf, man
        self._version = str(version)  # The version of the docs, e.g. 2 or 3
        self._verbose = verbose  # Enable debug info

    @property
    def REPO_PATH(self) -> pathlib.Path:
        return pathlib.Path(self._repo)

    @property
    def VERSION_PATH(self) -> List[pathlib.Path]:
        version_map = {
            "2": ["SDL2", "SDL2_image", "SDL2_mixer", "SDL2_net", "SDL2_ttf"],
            "3": ["SDL3", "SDL3_image", "SDL3_mixer", "SDL3_net", "SDL3_ttf"],
        }
        return [self.REPO_PATH / v for v in version_map[self._version]]

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
        self.logger.debug(f"Conversion Path: {self.ROOT_PATH}")
        self.logger.debug(f"Conversion Type: {self._type}")
        self.logger.debug(f"Conversion Version: {self._version}")
        # Automated parameters
        self.logger.debug(f"Repository Path: {base.REPO_PATH}")
        self.logger.debug(f"Version Paths: {base.VERSION_PATH}")
        self.logger.debug(f"Text Path: {base.TEXT_PATH}")
        self.logger.debug(f"PDF Path: {base.PDF_PATH}")
        self.logger.debug(f"Man Path: {base.MAN_PATH}")

    def test(self) -> None:
        prerequisites = ["git", "html2text", "pandoc", "xelatex"]
        self.logger.debug(f"Required Prerequisites: {prerequisites}")
        self.logger.debug("Asserting prerequisite discovery...")
        for requisite in prerequisites:
            if not shutil.which(requisite):
                self.logger.error(f"{requisite} not found. Please install it.")
                exit(1)
        self.logger.info("Prerequisite discovery completed successfully.")

    def run(self, args: List[str]) -> subprocess.CompletedProcess[Any]:
        # Restrict caller to passing in args
        params = {"check": True, "capture_output": True, "text": True}

        try:
            # Allow caller to handle result
            return subprocess.run(args, **params)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {e.cmd}")
            self.logger.error(f"Return code: {e.returncode}")
            self.logger.error(f"Output: {e.stdout}")
            self.logger.error(f"Error: {e.stderr}")
            exit(1)

    def clone(self) -> None:
        if os.path.exists(self.REPO_PATH):
            self.logger.debug("SDL Wiki directory already exists. Pulling latest changes...")
            args = ["git", "-C", self.REPO_PATH, "pull", "origin", "main"]
        else:
            self.logger.debug("Cloning SDL Wiki repository...")
            args = ["git", "clone", f"https://github.com/{self.REPO_PATH}", self.REPO_PATH]
        self.run(args)
        self.logger.info("SDL Wiki repository is up to date.")


if __name__ == "__main__":
    base = WikiBase(repo=".", root=".", _type="text", version="2", verbose=True)
    base.log()  # Always log before doing anything else
    base.test()
    result = base.run(["echo", "hello,", " world!"])
    print(result.stdout.strip())
    base.clone()
