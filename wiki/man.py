"""
Copyright © 2023 Austin Berrio
Module: wiki.man
Description:
"""

import datetime
import os
import pathlib
from typing import List

from wiki.base import WikiBase
from wiki.params import WikiParameters


class SDLWikiTextToMan(WikiBase):
    def __init__(self, params: WikiParameters):
        super().__init__(params)

    def generate_meta_data(self, file_path: pathlib.Path) -> List[str]:
        with open(file_path, "r") as source:
            # seek out the first line that starts with a # character and exit
            title = None
            lines = source.readlines()
            for line in lines:
                # search for the title, e.g. `# Some Title`
                if line[0] == "#" and line[1] == " ":
                    # text has already been preprocessed and normalized to unicode NFCK
                    # line is already a string, skip forward 2 chars and strip whitespace
                    title = line[2:].strip()
                    break  # exit loop as soon as we have a title
        return [
            "--metadata",
            f"title={title}",
            "--metadata",
            "section=3",
            "--metadata",
            f"date={datetime.date.today().isoformat()}",
            "--metadata",
            "source=SDL Wiki",
            "--metadata",
            "manual=SDL Library Manual",
        ]

    def convert(self) -> None:
        self.logger.info("Converting Markdown to Man pages...")
        for version_dir in self.params.IR_VERSION_DIRS:
            for root, _, files in os.walk(version_dir):
                for file in files:
                    if file.endswith(".md"):
                        md_file = pathlib.Path(root) / file
                        man_file = self.params.MAN_OUTPUT_DIR / md_file.with_suffix(".1").name
                        metadata = self.generate_meta_data(md_file)
                        self.logger.debug(f"Converting {md_file} to {man_file}")
                        args = [
                            "pandoc",
                            str(md_file),
                            "-s",
                            "-t",
                            "man",
                            "-o",
                            str(man_file),
                        ] + metadata
                        self.run(args)
        self.logger.info(f"Man pages saved in {self.params.MAN_OUTPUT_DIR}")
