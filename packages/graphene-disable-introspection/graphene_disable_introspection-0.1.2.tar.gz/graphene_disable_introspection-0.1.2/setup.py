#!/usr/bin/env python3
import os

from setuptools import setup

about = {}  # type: ignore
root = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(root, "graphene_disable_introspection", "__version__.py")) as f:
    exec(f.read(), about)

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name=about["__title__"],
    packages=["graphene_disable_introspection"],
    version=about["__version__"],
    license=about["__license__"],
    description=about["__description__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    download_url="https://github.com/Paprikaschote/graphene-disable-introspection/archive/refs/tags/v0.1.2.tar.gz",
    keywords=[
        "django",
        "graphene",
        "graphql",
        "introspection",
        "middleware",
        "__schema",
        "disable",
        "security",
    ],
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
    ],
)
