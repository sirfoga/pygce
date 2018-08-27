# !/usr/bin/python3
# coding: utf-8

from setuptools import setup, find_packages


DESCRIPTION = \
    "pygce\n\n\
    A tool to export, save, and analyze your  Garmin Connect data.\n\
    \n\
    Install\n\n\
    - $ python3 setup.py (install from source)\n\
    \n\
    Questions and issues\n\n\
    The github issue tracker is only for bug reports and feature requests.\
    Anything else, such as questions for help in using the tool, should be posted in StackOverflow.\n\
    \n\
    License: Apache License Version 2.0, January 2004"


setup(
    name="pygce",
    version="1.9.8",
    author="sirfoga",
    author_email="sirfoga@protonmail.com",
    description="pygce is an unofficial Garmin Connect data exporter.",
    long_description=DESCRIPTION,
    keywords="garmin data parser",
    url="https://github.com/sirfoga/pygce",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pygce = pygce.cli:main"
        ]
    },
    install_requires=[
        "bs4",
        "pyhal",
        "lxml",
        "numpy",
        "sklearn"
    ]
)
