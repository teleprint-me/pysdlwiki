"""
Copyright © 2023 Austin Berrio
Module: wiki.man
Description:
"""

import datetime
import os
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from wiki.base import WikiBase
from wiki.params import WikiParameters


class WikiTextToMan(WikiBase):
    def __init__(self, params: WikiParameters):
        super().__init__(params)

    def generate_meta_data(self, file_path: pathlib.Path) -> List[str]:
        """
        Extracts metadata for Pandoc by seeking out the first line that starts with a # character.
        """
        title = None
        with open(file_path, "r", encoding="utf-8") as source:
            for line in source:
                if line.startswith("# "):
                    title = line[2:].strip()  # Get the title and strip whitespace
                    break
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

    def process_file(self, md_file: pathlib.Path) -> None:
        """
        Converts a single Markdown file to a Man page using Pandoc.
        """
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

    def convert(self) -> None:
        """
        Converts Markdown files to Man pages in parallel.
        """
        processed = 0
        failed = 0

        self.logger.info("Starting parallel Markdown to Man page conversion...")
        # Collect all files to be processed
        files_to_process: List[pathlib.Path] = []
        for version_dir in self.params.IR_VERSION_DIRS:
            for root, _, files in os.walk(version_dir):
                for file in files:
                    if file.endswith(".md"):
                        files_to_process.append(pathlib.Path(root) / file)

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=(os.cpu_count() or 4)) as executor:
            futures = [executor.submit(self.process_file, file) for file in files_to_process]
            for future in as_completed(futures):
                try:
                    future.result()
                    processed += 1
                except Exception as e:
                    self.logger.error(f"Error processing file: {e}")
                    failed += 1

        self.logger.info(f"Processed: {processed}, Failed: {failed}")
        self.logger.info(f"Man pages saved in {self.params.MAN_OUTPUT_DIR}")
