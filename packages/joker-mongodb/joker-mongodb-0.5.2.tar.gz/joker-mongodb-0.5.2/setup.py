#!/usr/bin/env python3
# coding: utf-8
import os
import re

import setuptools
from setuptools import find_namespace_packages

# CAUTION:
# Do NOT import your package from your setup.py

_nsp = "joker"
_pkg = "mongodb"
_names = [_nsp, _pkg]
_names = [s for s in _names if s]


def read(filename):
    with open(filename) as f:
        return f.read()


def _find_version():
    names = _names + ["__init__.py"]
    root = os.path.dirname(__file__)
    path = os.path.join(root, *names)
    regex = re.compile(r"""^__version__\s*=\s*('|"|'{3}|"{3})([.\w]+)\1\s*(#|$)""")
    with open(path) as fin:
        for line in fin:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            mat = regex.match(line)
            if mat:
                return mat.groups()[1]
    raise ValueError("__version__ definition not found")


def _ensure_valid_native_namespace_package():
    path = os.path.join(os.path.split(__file__)[0], "joker/__init__.py")
    if os.path.exists(path):
        raise ImportError("not a valid native package")


config = {
    "name": "joker-mongodb",
    "version": _find_version(),
    "description": "access mongodb with handy utilities and fun",
    "keywords": "",
    "url": "https://github.com/frozflame/joker-mongodb",
    "author": "frozflame",
    "author_email": "frozflame@outlook.com",
    "license": "GNU General Public License (GPL)",
    "packages": find_namespace_packages(include=["joker.*"]),
    "zip_safe": False,
    "install_requires": read("requirements.txt"),
    "python_requires": ">=3.7.0",
    "classifiers": [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    # ensure copy static file to runtime directory
    "include_package_data": True,
    "long_description": read("README.md"),
    "long_description_content_type": "text/markdown",
}

if _nsp:
    config["namespace_packages"] = [_nsp]

_ensure_valid_native_namespace_package()
setuptools.setup(**config)
