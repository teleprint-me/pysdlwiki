"""
Copyright © 2023 Austin Berrio
Module: wiki.base
Description: Base class for converting SDL Wiki from HTML to a selected output format.
"""

import platform
import shutil
import subprocess
from typing import Any, List

from wiki.logger import AutoLogger
from wiki.params import WikiParameters


# NOTE: Not sure how I want to handle TEXT and PDF file paths just yet.
# Leaving these here as a reminder to my future self.
class WikiBase:
    def __init__(self, params: WikiParameters):
        self.params = params
        self.logger = AutoLogger.create(self.__class__.__name__, params.verbose)

    def log(self) -> None:
        os_info = {
            "OS Name": platform.system(),
            "Platform Release": platform.release(),
            "Conversion Path": self.params.ROOT_PATH,
            "Conversion Type": self.params.conversion_type,
            "Conversion Version": self.params.version,
            "Repository Path": self.params.REPO_PATH,
            "Version Paths": self.params.VERSION_PATH,
            "Text Path": self.params.TEXT_PATH,
            "PDF Path": self.params.PDF_PATH,
            "Man Path": self.params.MAN_PATH,
        }

        for key, value in os_info.items():
            self.logger.debug(f"{key}: {value}")

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
            result = subprocess.run(args, **params)
            self.logger.debug(f"Command succeeded: {args}")
            self.logger.debug(f"Output: {result.stdout}")
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {e.cmd}")
            self.logger.error(f"Return code: {e.returncode}")
            self.logger.error(f"Output: {e.stdout}")
            self.logger.error(f"Error: {e.stderr}")
            raise RuntimeError(f"Command failed: {' '.join(args)}") from e

    def clone(self) -> None:
        repo_dir = self.params.REPO_PATH
        if repo_dir.exists():
            self.logger.debug("SDL Wiki directory already exists. Pulling latest changes...")
            args = ["git", "-C", str(repo_dir), "pull", "origin", "main"]
        else:
            self.logger.debug("Cloning SDL Wiki repository...")
            repo_url = f"https://github.com/{self.params.repo}"
            args = ["git", "clone", repo_url, str(repo_dir)]
        self.run(args)
        self.logger.info("SDL Wiki repository is up to date.")


if __name__ == "__main__":
    params = WikiParameters(
        repo=".",
        root=".",
        conversion_type="text",
        version="2",
        verbose=True,
    )
    base = WikiBase(params)
    base.log()  # Always log before doing anything else
    base.test()
    result = base.run(["echo", "hello,", "world!"])
    print(result.stdout.strip())
    base.clone()
