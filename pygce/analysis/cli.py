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


import argparse
import os

from models import TimelineDataAnalysis


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(
        usage="-f <path to folder with data files to analyse>")
    parser.add_argument("-f", dest="folder_path", help="path to folder with data files to analyse", required=True)
    return parser


def parse_args(parser):
    """
    :param parser: ArgumentParser
        Object that holds cmd arguments.
    :return: tuple
        Values of arguments.
    """

    args = parser.parse_args()

    return str(args.folder_path)


def check_args(folder_path):
    """
    :param folder_path: str
        Path to folder with data files to analyse
    """

    assert os.path.exists(folder_path)

    return True


def main():
    folder_path = parse_args(create_args())
    if check_args(folder_path):
        for f in os.listdir(folder_path):
            file_path = os.path.join(folder_path, f)

            if os.path.isfile(file_path) and str(file_path).endswith(".csv"):
                gc = TimelineDataAnalysis(file_path)
                gc.show_correlation_matrix_of_data()
                # gc.predict_feature("SLEEP:deep_sleep_time")
    else:
        print("Error while parsing args.")


if __name__ == '__main__':
    main()