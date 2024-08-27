# SPDX-License-Identifier: Apache-2.0

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "docs/pypi-long-description.md").read_text()

# Read requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="j_chunker",
    version="0.1.1",
    author="Pavan Shiraguppi",
    author_email="shiraguppipavan@ibm.com",
    description="A package for chunking Japanese PDF documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.ibm.com/shiraguppipavan/J-Chunker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=required,
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "flake8",
            "black",
            "isort",
        ],
    },
    entry_points={
        "console_scripts": [
            "j_chunker=j_chunker.chunker:main",
        ],
    },
)