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

from hal.files.models import FileSystem, Document
from hal.ml.analysis import correlation
from hal.ml.data.parser import CSVParser

from models.garmin import utils  # 'from models.garmin import utils' when testing local script


class CorrelationAnalysis(object):
    """ Computes correlation of data"""

    def __init__(self, folder_data):
        """
        :param folder_data: str
            Path to folder with data to analyse
        """

        object.__init__(self)

        self.folder_data = folder_data

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
            n_array = [str(n).strip() for n in line[1:] if len(str(n).strip()) > 0]  # discard null value
            data.append(n_array)

        return headers, data

    @staticmethod
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
                    d[row][i] = utils.get_seconds(data[row][i])
        return d

    @staticmethod
    def fix_floats(headers, headers_to_fix, data):
        """
        :param headers: [] of str
            Column names of data
        :param headers_to_fix: [] of str
            Column names of data to fix the float format
        :param data: [] of []
            Raw data
        :return: [] of []
            Input data but with fixed floats in columns
        """

        d = data
        for i in range(len(headers)):
            if headers[i] in headers_to_fix:  # this columns id to be converted
                for row in range(len(data)):  # convert all rows of this column
                    d[row][i] = utils.parse_num(data[row][i])
        return d

    def save_correlation_matrix_of_file(self, f, title_image, headers_to_analyze):
        """
        :param f: str
            Path to file to save correlation matrix of
        :param title_image: str
            Title of output image
        :param headers_to_analyze: [] of str
            Compute correlation matrix of only these headers
        :return: void
            Saves correlation matrix of data of files in folder
        """

        if os.path.isfile(f) and str(f).endswith("csv"):
            print("Analysing file ", str(f))

            file_name = Document(f).name.strip()
            output_file_path = os.path.join(self.folder_data, file_name + ".png")  # save output as image
            headers, data = self.parse_csv(f)  # parse raw data
            correlation.save_correlation_matrix_of_columns(
                title_image,
                headers_to_analyze,  # headers to test
                headers,
                data,
                output_file_path
            )


class TimelineCorrelation(CorrelationAnalysis):
    """ Computes correlation of timeline data """

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

        CorrelationAnalysis.__init__(self, folder_data)

    def parse_csv(self, file_path):
        """
        :param file_path: str
            Path to file to parse
        :return: tuple [], [] of []
            Headers of csv file and data
        """

        headers, data = super(TimelineCorrelation, self).parse_csv(file_path)
        data = self.convert_time_columns(headers, self.TIME_HEADERS_TO_CONVERT, data)
        return headers, data

    def save_correlation_matrix_of_data(self):
        """
        :return: void
            Saves correlation matrix of data of files in folder
        """

        for f in FileSystem.ls(self.folder_data, False, False):
            self.save_correlation_matrix_of_file(f, "Garmin timeline data " + Document(f).name.strip(),
                                                 self.HEADERS_TO_ANALYZE)


class ActivitiesCorrelation(CorrelationAnalysis):
    """  Computes correlation of activities data """

    HEADERS_TO_ANALYZE = [
        "Distance",
        "Time",
        "Avg Speed(Avg Pace)",
        "Max Speed(Best Pace)",
        "Elevation Gain",
        "Avg HR",
        "Max HR",
        "Avg Run Cadence",
        "Max Run Cadence",
        "Calories",
        "Training Effect"
    ]  # get correlation analysis only for these columns
    TIME_HEADERS_TO_CONVERT = [
        "Time",
        "Avg Speed(Avg Pace)",
        "Max Speed(Best Pace)"
    ]  # columns of data file to convert from time format to float
    HEADERS_WITH_MALFORMED_FLOATS = [
        "Distance",
        "Training Effect"
    ]  # columns with malformed floats values

    def __init__(self, folder_data):
        """
        :param folder_data: str
            Path to folder with data to analyse
        """

        CorrelationAnalysis.__init__(self, folder_data)

    def parse_csv(self, file_path):
        """
        :param file_path: str
            Path to file to parse
        :return: tuple [], [] of []
            Headers of csv file and data
        """

        headers, data = super(ActivitiesCorrelation, self).parse_csv(file_path)
        data = self.convert_time_columns(headers, self.TIME_HEADERS_TO_CONVERT, data)
        data = self.fix_floats(headers, self.HEADERS_WITH_MALFORMED_FLOATS, data)
        return headers, data

    def save_correlation_matrix_of_data(self):
        """
        :return: void
            Saves correlation matrix of data of files in folder
        """

        for f in FileSystem.ls(self.folder_data, False, False):
            self.save_correlation_matrix_of_file(f, "Garmin activities data " + Document(f).name.strip(),
                                                 self.HEADERS_TO_ANALYZE)


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
        driver = ActivitiesCorrelation(folder_path)
        driver.save_correlation_matrix_of_data()
    else:
        print("Error while parsing args.")


if __name__ == '__main__':
    main()
