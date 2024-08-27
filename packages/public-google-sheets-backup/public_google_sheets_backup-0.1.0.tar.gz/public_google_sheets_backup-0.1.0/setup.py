# setup.py

from setuptools import setup, find_packages
import re
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'src', 'public_google_sheets_backup', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
    version_match = re.search(r'^[\s]*__version__[\s]*=[\s]*["\']([^"\']*)["\']', content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name="public-google-sheets-backup",
    version=get_version(),
    author="Yuan-Yi Chang",
    author_email="changyy.csie@gmail.com",
    description="A tool to backup and export public Google Sheets without authentication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/changyy/py-public-google-sheets-backup",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "public-google-sheets-backup=public_google_sheets_backup.cli:main",
            "public-gsheets-backup=public_google_sheets_backup.cli:main",
            "gsheets-backup=public_google_sheets_backup.cli:main",
            "gsheets-export=public_google_sheets_backup.cli:main",
            "gsheets-export-csv=public_google_sheets_backup.cli:csv_export",
            "gsheets-export-tsv=public_google_sheets_backup.cli:tsv_export",
            "google-sheets-export-csv=public_google_sheets_backup.cli:csv_export",
            "google-sheets-export-tsv=public_google_sheets_backup.cli:tsv_export",
        ],
    },
)
