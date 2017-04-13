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
from datetime import datetime

from hal.files.models import FileSystem, Document
from hal.ml.analysis import correlation
from hal.ml.data.parser import CSVParser


def get_seconds(s):
    """
    :param s: str
        Datetime in the form %H:%M:%S
    :return: int
        Seconds in time
    """

    t = datetime.strptime(str(s).strip(), "%H:%M:%S").time()  # get time
    total_seconds = t.second
    total_seconds += t.minute * 60.0
    total_seconds += t.hour * 60.0 * 60.0
    return total_seconds


def convert_time_columns(headers, headers_to_convert, data):
    """
    :param headers: [] of str
        Column names of data
    :param headers_to_convert: [] of str
        Column names of data to convert from time format to float
    :param data: [] of []
        Raw data
    :return: [] of []
        Input data but with converted time columns
    """

    d = data
    for i in range(len(headers)):
        if headers[i] in headers_to_convert:  # this columns id to be converted
            for row in range(len(data)):  # convert all rows of this column
                d[row][i] = get_seconds(data[row][i])
    return d


class CorrelationAnalysis(object):
    """ Computes correlation of data """

    HEADERS_TO_ANALYZE = [
        "SUMMARY:kcal_count",
        "STEPS:distance",
        "SLEEP:light_sleep_time",
        "BREAKDOWN:sleeping",
        "BREAKDOWN:highly_active",
        "ACTIVITIES:kcal",
        "BREAKDOWN:active",
        "STEPS:total",
        "STEPS:avg",
        "BREAKDOWN:sedentary",
        "SLEEP:awake_sleep_time",
        "SLEEP:total_sleep_time",
        "SLEEP:deep_sleep_time",
        "ACTIVITIES:duration",
        "ACTIVITIES:distance",
        "STEPS:goal",
        "SLEEP:night_sleep_time"
    ]  # get correlation analysis only for these columns
    TIME_HEADERS_TO_CONVERT = [
        "SLEEP:nap_time",
        "SLEEP:light_sleep_time",
        "SLEEP:awake_sleep_time",
        "SLEEP:total_sleep_time",
        "SLEEP:deep_sleep_time",
        "SLEEP:night_sleep_time",
        "ACTIVITIES:duration"
    ]  # columns of data file to convert from time format to float

    def __init__(self, folder_data):
        """
        :param folder_data: str
            Path to folder with data to analyse
        """

        object.__init__(self)

        self.folder_data = folder_data

    def save_correlation_matrix_of_data(self):
        """
        :return: void
            Saves correlation matrix of data of files in folder
        """

        for f in FileSystem.ls(self.folder_data, False, False):
            if os.path.isfile(f) and str(f).endswith("csv"):
                print("Analysing file ", str(f))

                file_name = Document(f).name.strip()
                output_file_name = file_name + ".png"  # save output as image
                output_file_path = os.path.join(self.folder_data, output_file_name)

                try:
                    headers, data = self.parse_csv(f)  # parse raw data
                    correlation.save_correlation_matrix_of_columns(
                        "Correlation of Garmin data" + file_name,
                        self.HEADERS_TO_ANALYZE,  # headers to test
                        headers,
                        data,
                        output_file_path
                    )
                except Exception as e:
                    print("Cannot save correlation matrix of file \"", str(f), "\" because of")
                    print(str(e))

    def parse_csv(self, file_path):
        """
        :param file_path: str
            Path to file to parse
        :return: tuple [], [] of []
            Headers of csv file and data
        """

        raw_data = CSVParser(file_path).parse_data()
        headers = raw_data[0][1:]  # first row discarding time value
        headers = [h.strip() for h in headers]
        raw_data = raw_data[1:]  # discard headers row

        data = []
        for line in raw_data:  # parse raw data
            n_array = [str(n).strip() for n in line[1:] if len(str(n).strip()) > 1]  # discard null value
            data.append(n_array)

        data = convert_time_columns(headers, self.TIME_HEADERS_TO_CONVERT, data)
        return headers, data


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
        driver = CorrelationAnalysis(folder_path)
        driver.save_correlation_matrix_of_data()
    else:
        print("Error while parsing args.")


if __name__ == '__main__':
    main()
