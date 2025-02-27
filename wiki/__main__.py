"""
Copyright © 2023 Austin Berrio
Script: wiki.__main__
Description:
"""

import argparse

from wiki.base import WikiBase
from wiki.man import WikiTextToMan
from wiki.params import WikiParameters
from wiki.pdf import WikiTextToPDF
from wiki.text import WikiHTMLToText


class SDLWikiConverter(WikiBase):
    def __init__(self, params: WikiParameters):
        super().__init__(params)
        self.text = WikiHTMLToText(args)
        self.pdf = WikiTextToPDF(args)
        self.man = WikiTextToMan(args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert SDL Wiki documentation to Text, PDF, or Man format."
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug mode.")
    parser.add_argument(
        "--type",
        choices=["text", "pdf", "man"],
        default="pdf",
        help="Output format type. 'text' concatenates all Markdown files, 'pdf' generates a PDF document, and 'man' generates a Unix man page.",
    )
    parser.add_argument(
        "--version",
        choices=["2", "3"],
        default="2",
        help="SDL Wiki version. '2' for SDL2 documentation and '3' for SDL3 documentation.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    sdl_wiki = SDLWikiConverter(args)
    sdl_wiki.log()
    sdl_wiki.test()
    sdl_wiki.clone()

    sdl_wiki.text.convert()

    if args.type == "text":
        sdl_wiki.text.concatenate()
    elif args.type == "pdf":
        sdl_wiki.text.concatenate()
        sdl_wiki.pdf.convert()
    elif args.type == "man":
        sdl_wiki.man.convert()
    elif args.type == "man":
        sdl_wiki.man.convert()
