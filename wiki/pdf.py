"""
Copyright © 2023 Austin Berrio
Module: wiki.pdf
Description:
    Converts the SDL Wiki from the concatenated Markdown to PDF using pandoc.

Pipeline Overview:
    All steps require: TEXT: HTML | TEXT -> Normalize -> Sanitize -> TEXT
    Text to PDF: TEXT -> Concatenate -> Generate a PDF from the concatenated file.

Caveats:
    - The concatenated file must be used in order to preserve paging.
    - Pandoc is single threaded and can not be sped up as a result.
    - If multi-threading was applied, processing and converting on a page by page basis,
      it could be threaded, but would fail to preserve paging which is undesirable.
"""

from wiki.base import WikiBase
from wiki.params import WikiParameters


class WikiTextToPDF(WikiBase):
    def __init__(self, params: WikiParameters):
        super().__init__(params)

    def convert(self) -> None:
        self.logger.info(
            f"Converting {self.params.TEXT_OUTPUT_FILE} to {self.params.PDF_OUTPUT_FILE}..."
        )

        # Check if the input file exists and is readable
        if not self.params.TEXT_OUTPUT_FILE.is_file():
            self.logger.error(f"Input file does not exist: {self.params.TEXT_OUTPUT_FILE}")
            return

        args = [
            "pandoc",
            str(self.params.TEXT_OUTPUT_FILE),
            "-o",
            str(self.params.PDF_OUTPUT_FILE),
            "--pdf-engine=xelatex",
            "--from",
            "markdown-raw_tex",
            "--strip-comments",
            "--wrap=preserve",
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

        # Run the command and capture output
        result = self.run(args)

        # Log the stderr output in case of errors
        if result.returncode != 0:
            self.logger.error(f"Pandoc failed with error code {result.returncode}")
            self.logger.error(result.stderr)
        else:
            self.logger.info(f"PDF saved as {self.params.PDF_OUTPUT_FILE}")


if __name__ == "__main__":
    from wiki.text import WikiHTMLToText

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

    # Post-process text and output PDF file
    pdf = WikiTextToPDF(params)
    pdf.convert()
