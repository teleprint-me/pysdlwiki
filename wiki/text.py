"""
Module: wiki.text
Description: Converts the Wiki from HTML, if applicable, to Markdown. Sanitizes Markdown otherwise.
"""

import os
import pathlib
import unicodedata

import regex as re

from wiki.base import WikiBase
from wiki.logger import AutoLogger
from wiki.params import WikiParameters


# NOTE: This modifies files in place and is destructive as a result.
# This needs to be remedied ASAP. This class is super sensitive and is a rerequisite to every
# other step in the pipeline.
# The repository maintained by libsdl-org automates text generation.
# libsdl-org also makes the HTML available as an option.
# To keep this simple, I'm keeping the initial implementation single threaded, but it is slow.
# So a multi-threaded operation will be required in order speed things up.
# Pipeline may be one of 3 possible scenarios.
# All steps require TEXT -> Normalize -> Sanitize
# 1. HTML (Optional) -> TEXT -> Normalize -> Sanitize -> Concatenate
# 2. TEXT -> Normalize -> Sanitize -> Concatenate -> Generate a PDF from cat file
# 3. TEXT -> Normalize -> Sanitize -> Generate a MAN page from each TEXT file
class WikiHTMLToText(WikiBase):
    def __init__(self, params: WikiParameters):
        super().__init__(params)
        # NOTE: Not sure if logger needs to be overridden.

    @property
    def TEXT_FILE(self) -> pathlib.Path:
        return self.TEXT_PATH / f"SDL-Wiki-v{self.params.version}.md"

    def sanitize(self, text: str) -> str:
        comment = r"<!-- Horizontal line omitted for PDF and MAN -->"
        patterns = {
            r"\u201C": r"\"",  # Curly quote to straight quote
            r"\u201D": r"\"",  # Curly quote to straight quote
            r"^----$": comment,  # Horizontal line replacement
            r"^----\s*$": comment,  # Edge case for trailing spaces
            r"\[(.*?)\]\(.*?\)": r"\1",  # Inline links -> keep text
            r"\[([^\]]+)\]\[[^\]]+\]": r"\1",  # Reference links -> keep text
            r"^\[.*?\]:\s?.*?$": "",  # Remove link references
            r"\(\)": "",  # Remove empty parentheses
        }
        # Split the text blob into lines while preserving line breaks
        lines = text.splitlines()
        # We need to enumerate over a shallow copy to modify lines and track positions
        for n, line in enumerate(lines[:]):
            # Iterate over each pattern and substitute matched patterns
            for pattern, replacement in patterns.items():
                line = re.sub(pattern, replacement, line)
            # Substitute line for line using tracked positions
            lines[n] = line
        return "\n".join(lines)  # Join lines with preserved line breaks

    def normalize(self, text: str) -> str:
        normalized_text = unicodedata.normalize("NFKC", text)
        return normalized_text.strip()

    def html2text(self, html_file: pathlib.Path) -> str:
        self.logger.debug(f"Converting {html_file} to Markdown")
        args = [
            "html2text",
            "--no-wrap-links",
            "--wrap-tables",
            "--images-to-alt",
            str(html_file),
        ]
        return self.run(args).stdout

    def convert(self) -> None:
        self.logger.info("Converting HTML to Markdown...")
        for version_dir in self.VERSION_PATH:
            for root, _, files in os.walk(version_dir):
                for file in files:
                    file_path = pathlib.Path(root) / file
                    if file.endswith(".html"):
                        markdown = self.html2text(file_path)
                    if file.endswith(".md"):
                        with open(file_path, "r") as source:
                            markdown = source.read()
                    if markdown is None:
                        self.logger.debug(f"Skipping {file}...")
                        continue
                    # must normalize and then sanitize after initial processing
                    markdown = self.normalize(markdown)
                    markdown = self.sanitize(markdown)
                    text_file = file_path.with_suffix(".md")
                    with open(text_file, "w") as target:
                        # add a newline to the end of each file
                        target.write(markdown + "\n")
        self.logger.info("HTML to Markdown conversion completed.")

    def concatenate(self) -> None:
        self.logger.info("Concatenating Markdown files...")
        text_body = ""
        for version in self.VERSION_PATH:
            for root, _, files in os.walk(version):
                for file in sorted(files):
                    if file.endswith(".md"):
                        text_file = os.path.join(root, file)
                        self.logger.debug(f"Adding {text_file} to {self.TEXT_FILE}")
                        with open(text_file, "r") as source:
                            # add padding between each file
                            text_body += source.read() + "\n"
        with open(self.TEXT_FILE, "w") as target:
            target.write(text_body)
        self.logger.info(f"Combined Markdown saved as {self.TEXT_FILE}")
