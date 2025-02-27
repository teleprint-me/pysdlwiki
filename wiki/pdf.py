"""
Copyright © 2023 Austin Berrio
Module: wiki.pdf
Description:
    Converts the SDL Wiki from the concatenated Markdown to PDF using pandoc.

Pipeline Overview:
    All steps require: TEXT -> Normalize -> Sanitize
    Text to PDF: TEXT -> Concatenate -> Generate a PDF from the concatenated file.

Caveats:
    - The concatenated file must be used in order to preserve paging.
    - Pandoc is single threaded and can not be sped up as a result.
    - If multi-threading was applied, processing and converting on a page by page basis,
      it could be threaded, but would fail to preserve paging.
"""

import pathlib

from wiki.base import WikiBase
from wiki.params import WikiParameters


class WikiTextToPDF(WikiBase):
    def __init__(self, params: WikiParameters):
        super().__init__(params)

    @property
    def INPUT_FILE(self) -> pathlib.Path:
        return self.params.TEXT_PATH / f"SDL-Wiki-v{self.params.version}.md"

    @property
    def OUTPUT_FILE(self) -> pathlib.Path:
        return self.params.PDF_PATH / f"SDL-Wiki-v{self.params.version}.pdf"

    def convert(self) -> None:
        self.logger.info(f"Converting {self.INPUT_FILE} to {self.OUTPUT_FILE}...")
        args = [
            "pandoc",
            str(self.INPUT_FILE),
            "-o",
            str(self.OUTPUT_FILE),
            "--pdf-engine=xelatex",  # Convert markdown to tex
            "--from",
            "markdown-raw_tex",  # Preserve pre-processed text
            "--strip-comments",  # Remove auto-generated comments
            "--wrap=preserve",  # Preserve tex line breaks
            "-V",
            "geometry:margin=0.5in",
            "-V",
            "geometry:a4paper",
            "-V",
            "mainfont=Noto Sans Mono",
            "-V",
            "fontsize=10pt",
            "-V",
            "linestretch=1.2",
            "-V",
            "colorlinks=true",
            "-V",
            "linkcolor=blue",
        ]
        self.run(args)
        self.logger.info(f"PDF saved as {self.OUTPUT_FILE}")
