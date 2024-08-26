#!/usr/bin/env python

import os
import re

from setuptools import setup, find_packages


def find_version(*segments):
    root = os.path.abspath(os.path.dirname(__file__))
    abspath = os.path.join(root, *segments)
    with open(abspath, "r") as file:
        content = file.read()
    match = re.search(r"^__version__ = ['\"]([^'\"]+)['\"]", content, re.MULTILINE)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string!")


setup(
    author="Richard Davis",
    author_email="crashvb@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: POSIX :: Linux",
    ],
    description="Consolidation of logging utilities.",
    extras_require={
        "dev": [
            "black",
            "coveralls",
            "pylint",
            "pytest",
            "pytest-cov",
            "twine",
            "wheel",
        ]
    },
    include_package_data=True,
    install_requires=["click"],
    keywords="crashvb logging utilities",
    license="Apache License 2.0",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    name="crashvb_logging_utilities",
    packages=find_packages(),
    package_data={"": ["data/*"]},
    project_urls={
        "Bug Reports": "https://github.com/server27nw/crashvb-logging-utilities/issues",
        "Source": "https://github.com/server27nw/crashvb-logging-utilities",
    },
    tests_require=["pytest"],
    test_suite="tests",
    url="https://pypi.org/project/crashvb-logging-utilities/",
    version=find_version("crashvb_logging_utilities", "__init__.py"),
)
