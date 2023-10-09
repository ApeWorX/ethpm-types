#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent.absolute()

extras_require = {
    "test": [  # `test` GitHub Action jobs uses this
        "pytest>=6.0",  # Core testing package
        "pytest-xdist",  # multi-process runner
        "pytest-cov",  # Coverage analyzer plugin
        "hypothesis>=6.2.0,<7.0",  # Strategy-based fuzzer
        # Test-only deps
        "PyGithub>=1.54,<2.0",  # Necessary to pull official schema from github
        "hypothesis-jsonschema==0.19.0",  # Fuzzes based on a json schema
        "pysha3>=1.0.2,<2.0.0",  # Backend for eth-hash
    ],
    "lint": [
        "black>=23.9.1,<24",  # auto-formatter and linter
        "mypy>=1.5.1,<2",  # Static type analyzer
        "types-setuptools",  # Needed due to mypy typeshed
        "types-requests",  # Needed due to mypy typeshed
        "flake8>=6.1.0,<7",  # Style linter
        "flake8-breakpoint>=1.1.0",  # detect breakpoints left in code
        "flake8-print>=4.0.0",  # detect print statements left in code
        "isort>=5.10.1,<5.11",  # Import sorting linter
    ],
    "doc": [
        "myst-parser>=0.17.0,<0.18",  # Tools for parsing markdown files in the docs
        "sphinx-click>=3.1.0,<4.0",  # For documenting CLI
        "Sphinx>=4.4.0,<5.0",  # Documentation generator
        "sphinx_rtd_theme>=1.0.0,<2",  # Readthedocs.org theme
        "sphinxcontrib-napoleon>=0.7",  # Allow Google-style documentation
    ],
    "release": [  # `release` GitHub Action job uses this
        "setuptools",  # Installation tool
        "wheel",  # Packaging tool
        "twine",  # Package upload tool
    ],
    "dev": [
        # commitizen: Manage commits and publishing releases
        (here / "cz-requirement.txt").read_text().strip(),
        "pre-commit",  # Ensure that linters are run prior to committing
        "pytest-watch",  # `ptw` test watcher/runner
        "IPython",  # Console for interacting
        "ipdb",  # Debugger (Must use `export PYTHONBREAKPOINT=ipdb.set_trace`)
    ],
}

# NOTE: `pip install -e .[dev]` to install package
extras_require["dev"] = (
    extras_require["test"]
    + extras_require["lint"]
    + extras_require["release"]
    + extras_require["dev"]
)

with open("./README.md") as readme:
    long_description = readme.read()


setup(
    name="ethpm-types",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="""ethpm_types: Implementation of EIP-2678""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ApeWorX Ltd.",
    author_email="admin@apeworx.io",
    url="https://github.com/ApeWorX/ethpm-types",
    include_package_data=True,
    install_requires=[
        "hexbytes>=0.3.0,<1",
        "pydantic>=1.10.7,!=2.0.*,!=2.1.*,!=2.2.*,<3",
        "eth-utils>=2.1.0,<3",
        "py-cid>=0.3.0,<0.4",
        "requests>=2.29.0,<3",
    ],
    python_requires=">=3.8,<4",
    extras_require=extras_require,
    py_modules=["ethpm_types"],
    license="Apache-2.0",
    zip_safe=False,
    keywords="ethereum",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"ethpm_types": ["py.typed"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
