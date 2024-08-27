# py-public-google-sheets-backup

![PyPI](https://img.shields.io/pypi/v/public-google-sheets-backup.svg)

Python tool for effortless backup and export of public Google Sheets without authentication. Supports CSV and TSV formats.

## Features

- Export public Google Sheets without requiring authentication or API keys
- Support for both CSV and TSV export formats
- Simple command-line interface
- Lightweight with minimal dependencies

## Installation

```bash
pip install public-google-sheets-backup
```

# Usage

## Basic usage

```bash
public-gsheets-backup https://docs.google.com/spreadsheets/d/your_sheet_id_here/edit
```

## Export as TSV

```bash
public-gsheets-backup https://docs.google.com/spreadsheets/d/your_sheet_id_here/edit --type tsv
```

## Specify output directory

```bash
public-gsheets-backup https://docs.google.com/spreadsheets/d/your_sheet_id_here/edit -o /path/to/output
```

# Development

To set up the development environment:

1. Clone the repository

```bash
git clone https://github.com/changyy/py-public-google-sheets-backup
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate 
```

3. Install the package in editable mode with development dependencies:

```bash
pip install -e .
```

# Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

# License

This project is licensed under the MIT License - see the LICENSE file for details.
