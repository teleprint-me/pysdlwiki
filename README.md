# PySDLWiki

**PySDLWiki** is a Python tool that converts the SDL Wiki documentation to a
selected output format: **Text**, **PDF**, or **Man pages**.

The pipeline efficiently processes the documentation using a three-stage
conversion process:

- **HTML to Text**: Converts HTML to normalized and sanitized Markdown.
- **Text to PDF**: Converts concatenated Markdown to a paginated PDF.
- **Text to Man**: Converts each Markdown file to a Unix Man page.

The design is optimized for:

- **Performance**: Leveraging parallel processing for text and man page
  conversion.
- **Maintainability**: Modular structure for ease of extension and maintenance.
- **Usability**: Simple CLI interface with clear options and help messages.

## Features

- **Parallelized HTML to Text conversion** for faster preprocessing.
- **High-quality PDF output** with proper pagination using `pandoc` and
  `xelatex`.
- **Man Page generation** for Unix-based systems.
- **Supports SDL2 and SDL3 Documentation** versions.
- **Verbose Logging** for detailed insights and debugging.

## Installation

This project requires the following dependencies:

- **Python 3.8+**
- **regex**: Python package for Regular Expressions matching.
- **html2text**: Python package for HTML to Markdown conversion
- **Pandoc**: `pandoc` and `xelatex` are required for PDF generation

Install the required Python dependencies:

```sh
pip install -r requirements.txt
```

Ensure the required system dependencies are installed:

```sh
# On Debian/Ubuntu-based systems:
sudo apt install pandoc texlive-xetex

# On Arch-based systems:
sudo pacman -S pandoc-cli texlive-xetex
```

## Usage

The CLI is simple and user-friendly:

```sh
python -m wiki -h
```

**Example Commands:**

1. **Convert to Text:**

```sh
python -m wiki --type text --version 2 --verbose
```

2. **Convert to PDF:**

```sh
python -m wiki --type pdf --version 3
```

3. **Convert to Man Pages:**

```sh
python -m wiki --type man --version 2 --verbose
```

## Output Structure

The output is organized as follows:

```
output/
├── text/
│   ├── intermediate/         # Intermediate representations (IR) of Markdown files
│   └── SDL-Wiki-v{version}.md # Concatenated Markdown file
├── pdf/
│   └── SDL-Wiki-v{version}.pdf
└── man/
    └── *.1                  # Generated Man pages
```

## Example Output

```sh
python -m wiki --type man --version 2 --verbose
```

This command generates Man pages for SDL2 documentation in `output/man/`. You
can view the Man pages using:

```sh
man output/man/SDL_AllocFormat.1
```

## Development and Contribution

Feel free to open issues or submit pull requests. This project was developed to
simplify SDL Wiki documentation conversion while maintaining high-quality
output. Contributions are always welcome!

## License

This project is licensed under **AGPL-3.0**. See the [LICENSE](LICENSE) file for
details.
