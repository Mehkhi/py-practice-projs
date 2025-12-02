"""
Setup script for the email sender package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="email-sender",
    version="1.0.0",
    author="Python Practice Projects",
    author_email="practice@pythonprojects.com",
    description="A professional CLI tool for sending emails with attachments and batch processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/python-practice-projects/email-sender",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "email-validator>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "email-sender=email_sender.main:main",
        ],
    },
    keywords="email smtp cli batch attachments html templates",
    project_urls={
        "Bug Reports": "https://github.com/python-practice-projects/email-sender/issues",
        "Source": "https://github.com/python-practice-projects/email-sender",
        "Documentation": "https://github.com/python-practice-projects/email-sender#readme",
    },
)
