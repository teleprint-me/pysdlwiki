"""
Module: wiki.text
Description:
    Converts the SDL Wiki from HTML to Markdown, if applicable, otherwise sanitizes existing Markdown.
    This is a prerequisite step for all other stages in the pipeline.

Pipeline Overview:
    All steps require: TEXT -> Normalize -> Sanitize
    There are three possible scenarios:
        1. HTML (Optional) -> TEXT -> Concatenate all TEXT files into a single TEXT file.
        2. TEXT -> Concatenate -> Generate a PDF from the concatenated file
        3. TEXT -> Generate a MAN page from each TEXT file

Caveats:
    - This class modifies files in place and is destructive as a result.
    - The repository maintained by libsdl-org automates text generation and makes the HTML available as an option.
    - To keep this simple, the initial implementation is single-threaded but may require multi-threading for performance.
    - This class is highly sensitive, and even minor changes can cause unintended ripple effects.
"""

import os
import pathlib
import unicodedata

import regex as re

from wiki.base import WikiBase
from wiki.params import WikiParameters


class WikiHTMLToText(WikiBase):
    def __init__(self, params: WikiParameters):
        super().__init__(params)

    @property
    def TEXT_FILE(self) -> pathlib.Path:
        return self.params.TEXT_PATH / f"SDL-Wiki-v{self.params.version}.md"

    def sanitize(self, text: str) -> str:
        """
        Sanitizes Markdown text by applying various regex patterns to remove or replace unwanted content.
        """
        patterns = {
            r"\u201C": r"\"",  # Curly quote to straight quote
            r"\u201D": r"\"",  # Curly quote to straight quote
            r"^----$": r"<!-- Horizontal line omitted for PDF and MAN -->",
            r"^----\s*$": r"<!-- Horizontal line omitted for PDF and MAN -->",
            r"\[(.*?)\]\(.*?\)": r"\1",  # Inline links -> keep text
            r"\[([^\]]+)\]\[[^\]]+\]": r"\1",  # Reference links -> keep text
            r"^\[.*?\]:\s?.*?$": "",  # Remove link references
            r"\(\)": "",  # Remove empty parentheses
        }
        compiled_patterns = [(re.compile(pat), repl) for pat, repl in patterns.items()]
        lines = text.splitlines()
        for n, line in enumerate(lines):
            for pattern, replacement in compiled_patterns:
                line = pattern.sub(replacement, line)
            lines[n] = line
        return "\n".join(lines)

    def normalize(self, text: str) -> str:
        """
        Normalizes text to NFKC form for consistent Unicode handling and removes leading/trailing whitespace.
        """
        return unicodedata.normalize("NFKC", text).strip()

    def html2text(self, html_file: pathlib.Path) -> str:
        """
        Converts an HTML file to Markdown using html2text.
        """
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
        """
        Converts HTML files to Markdown and sanitizes existing Markdown files.
        """
        self.logger.info("Converting HTML to Markdown...")
        for version_dir in self.params.VERSION_PATH:
            self._process_version_dir(version_dir)
        self.logger.info("HTML to Markdown conversion completed.")

    def _process_version_dir(self, version_dir: pathlib.Path) -> None:
        """
        Processes all files in a version directory, converting or sanitizing Markdown as needed.
        """
        for root, _, files in os.walk(version_dir):
            for file in files:
                self._process_file(root, file)

    def _process_file(self, root: str, file: str) -> None:
        """
        Processes a single file: converts HTML to Markdown or sanitizes existing Markdown.
        """
        file_path = pathlib.Path(root) / file
        markdown = None
        if file.endswith(".html"):
            markdown = self.html2text(file_path)
        elif file.endswith(".md"):
            markdown = file_path.read_text(encoding="utf-8")

        if markdown is None:
            self.logger.warning(f"Skipping unsupported file: {file}")
            return

        # Normalize and sanitize the Markdown content
        markdown = self.normalize(markdown)
        markdown = self.sanitize(markdown)

        # Write the processed content back to file
        text_file = file_path.with_suffix(".md")
        text_file.write_text(markdown + "\n", encoding="utf-8")

    def concatenate(self) -> None:
        """
        Concatenates all Markdown files into a single combined Markdown file.
        """
        self.logger.info("Concatenating Markdown files...")
        text_body = ""
        for version in self.params.VERSION_PATH:
            for root, _, files in os.walk(version):
                for file in sorted(files):
                    if file.endswith(".md"):
                        text_file = pathlib.Path(root) / file
                        self.logger.debug(f"Adding {text_file} to {self.TEXT_FILE}")
                        text_body += text_file.read_text(encoding="utf-8") + "\n"
        self.TEXT_FILE.write_text(text_body, encoding="utf-8")
        self.logger.info(f"Combined Markdown saved as {self.TEXT_FILE}")


if __name__ == "__main__":
    params = WikiParameters(repo=".", root=".", conversion_type="text", version="2", verbose=True)
    converter = WikiHTMLToText(params)
    converter.log()  # Log system info and parameters before starting
    converter.test()
    converter.clone()  # Ensure the repo exists
    converter.convert()
    converter.concatenate()
    converter.concatenate()
