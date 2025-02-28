"""
Copyright © 2023 Austin Berrio
Module: wiki.text
Description:
    Converts the SDL Wiki from HTML to Markdown, if applicable, otherwise sanitizes existing Markdown.
    Outputs processed files to a separate directory to preserve the original files.

Pipeline Overview:
    All steps require: TEXT -> Normalize -> Sanitize
    There are three possible scenarios:
        1. HTML (Optional) -> TEXT -> Concatenate TEXT files.
        2. TEXT -> Concatenate -> Generate a PDF from the concatenated file
        3. TEXT -> Generate a MAN page from each TEXT file

Caveats:
    - This class is highly sensitive, and even minor changes can cause unintended ripple effects.
"""

import os
import pathlib
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import regex as re

from wiki.base import WikiBase
from wiki.params import WikiParameters


class WikiHTMLToText(WikiBase):
    def __init__(self, params: WikiParameters):
        super().__init__(params)

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
        Converts HTML files to Markdown and sanitizes existing Markdown files in parallel.
        Outputs to the intermediate directory to preserve original files.
        """
        self.logger.info("Starting parallel HTML to Markdown conversion...")

        # Collect all files to be processed
        files_to_process: List[pathlib.Path] = []
        for version_dir in self.params.VERSION_DIRS:
            for root, _, files in os.walk(version_dir):
                for file in files:
                    file_path = pathlib.Path(root) / file
                    files_to_process.append(file_path)

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=(os.cpu_count() or 4)) as executor:
            futures = [executor.submit(self.process_file, file) for file in files_to_process]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Error processing file: {e}")

        self.logger.info("HTML to Markdown conversion completed in parallel.")

    def process_file(self, file_path: pathlib.Path) -> None:
        """
        Processes a single file: converts HTML to Markdown or sanitizes existing Markdown.
        Saves processed files in the intermediate directory.
        """
        relative_path = file_path.relative_to(self.params.REPO_PATH)
        output_file = self.params.IR_DIR / relative_path.with_suffix(".md")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        markdown = None
        if file_path.suffix == ".html":
            markdown = self.html2text(file_path)
        elif file_path.suffix == ".md":
            markdown = file_path.read_text(encoding="utf-8")

        if markdown is None:
            self.logger.warning(f"Skipping unsupported file: {file_path}")
            return

        # Normalize and sanitize the Markdown content
        markdown = self.normalize(markdown)
        markdown = self.sanitize(markdown)

        # Write the processed content to the IR directory
        output_file.write_text(markdown + "\n", encoding="utf-8")
        self.logger.debug(f"Processed {file_path} -> {output_file}")

    def concatenate(self) -> None:
        """
        Concatenates all Markdown files into a single combined Markdown file.
        """
        self.logger.info("Concatenating Markdown files...")
        text_body = ""
        for version in self.params.IR_VERSION_DIRS:
            for root, _, files in os.walk(version):
                for file in sorted(files):
                    if file.endswith(".md"):
                        text_file = pathlib.Path(root) / file
                        self.logger.debug(f"Adding {text_file} to {self.params.TEXT_OUTPUT_FILE}")
                        text_body += text_file.read_text(encoding="utf-8") + "\n"
        self.params.TEXT_OUTPUT_FILE.write_text(text_body, encoding="utf-8")
        self.logger.info(f"Combined Markdown saved as {self.params.TEXT_OUTPUT_FILE}")


if __name__ == "__main__":
    params = WikiParameters(
        repo=".",
        root=".",
        conversion_type="text",
        version="2",
        verbose=True,
    )

    # Pre-process text and output intermediary representations
    text = WikiHTMLToText(params)
    text.log()  # Log system info and parameters before starting
    text.test()
    text.clone()  # Ensure the repo exists
    text.convert()
    text.concatenate()
