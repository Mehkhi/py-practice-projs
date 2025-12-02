from setuptools import setup, find_packages

setup(
    name="cli-notes-with-search",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "cryptography>=41.0.0",
    ],
    entry_points={
        "console_scripts": [
            "notes=cli_notes_with_search.main:cli",
        ],
    },
)
