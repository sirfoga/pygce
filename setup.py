# !/usr/bin/python3
# coding: utf-8

# Copyright 2017 Stefano Fogarollo
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from setuptools import setup, find_packages


DESCRIPTION = \
    "pygce\n\n\
    A tool to export your data from Garmin Connect.\n\
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
    version="0.0.5",
    author="sirfoga",
    author_email="sirfoga@protonmail.com",
    description="pygce is an unofficial Garmin Connect data exporter.",
    long_description=DESCRIPTION,
    license="Apache License, Version 2.0",
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
        "lxml"
    ]
)
