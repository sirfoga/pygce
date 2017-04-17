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


import matplotlib.pyplot as plt
from hal.files.models import Document
from hal.ml.analysis import correlation
from hal.ml.data.parser import parse_csv_file
from hal.ml.utils import matrix as m_utils
from sklearn import linear_model

from pygce.models.garmin import utils  # 'from models.garmin import utils' when testing local script


class GarminDataFilter(object):
    """ Parses and fixes raw data """

    def __init__(self, dataset_file):
        """
        :param dataset_file: str
            Path to folder with data to analyse
        """

        object.__init__(self)

        self.dataset_file = dataset_file

    def parse_csv(self):
        """
        :return: tuple [], [] of []
            Headers of csv file and data
        """

        return parse_csv_file(self.dataset_file)

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


class StatsAnalysis(GarminDataFilter):
    """ Computes correlation of data"""

    def __init__(self, dataset_file):
        """
        :param dataset_file: str
            Path to folder with data to analyse
        """

        GarminDataFilter.__init__(self, dataset_file)

    def show_correlation_matrix(self, title_image, headers_to_analyze):
        """
        :param title_image: str
            Title of output image
        :param headers_to_analyze: [] of str
            Compute correlation matrix of only these headers
        :return: void
            Shows correlation matrix of data of files in folder
        """

        print("Computing correlation matrix of file ", str(self.dataset_file))
        headers, data = self.parse_csv()  # parse raw data
        correlation.show_correlation_matrix_of_columns(
            title_image,
            headers_to_analyze,  # headers to test
            headers,
            data
        )


class TimelineDataAnalysis(StatsAnalysis):
    """ Machine-learn timeline data """

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

    def __init__(self, dataset_file):
        """
        :param dataset_file: str
            Path to folder with data to analyse
        """

        StatsAnalysis.__init__(self, dataset_file)

    def parse_csv(self):
        """
        :return: tuple [], [] of []
            Headers of csv file and data
        """

        headers, data = super(TimelineDataAnalysis, self).parse_csv()
        data = self.convert_time_columns(headers, self.TIME_HEADERS_TO_CONVERT, data)
        return headers, data

    def show_correlation_matrix_of_data(self):
        """
        :return: void
            Shows correlation matrix of data of files in folder
        """

        self.show_correlation_matrix("Garmin timeline data " + Document(self.dataset_file).name.strip(),
                                     self.HEADERS_TO_ANALYZE)

    def predict_feature(self, feature):
        """
        :param feature: str
            Name of feature (column name) to predict
        :return: TODO
            TODO
        """

        headers, raw_data = self.parse_csv()  # get columns names and raw data
        clf = linear_model.LinearRegression()  # model to fit data

        print("Predicting \"", feature, "\"")
        x_matrix_features = self.HEADERS_TO_ANALYZE
        x_matrix_features.remove(feature)  # do NOT include feature to predict in input matrix
        x_data = m_utils.get_subset_of_matrix(x_matrix_features, headers, raw_data)  # input matrix
        y_data = m_utils.get_subset_of_matrix([feature], headers, raw_data)  # output matrix
        clf.fit(x_data, y_data)

        coefficients = {}  # dict feature -> coefficient
        for i in range(len(x_matrix_features)):
            coefficients[x_matrix_features[i]] = clf.coef_[0][i]

        self.show_bar_chart("Linear fit of " + feature, [k for k in coefficients.keys()], coefficients.values(),
                            "Coefficient")

    def cluster_analyze(self):
        """
        :return: void
            Computes cluster analysis: see days based on differences.
            Each day is different from one another, there are days where you trained more, others where you ate more ...
            The goal is to divide your days into categories (e.g highly-active, active ...) based on data logs.
        """

        pass

    @staticmethod
    def show_bar_chart(title, x_labels, y_values, y_label):
        """
        :param title: str
            Title of chart
        :param x_labels: [] of str
            Names for each variable
        :param y_values: [] of float
            Values of x labels
        :param y_label: str
            Label of y axis
        :return: void
            Show bar chart
        """

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        plt.title(title)
        plt.grid(True)
        plt.gcf().subplots_adjust(bottom=0.25)  # include long x-labels

        ax1.set_xticks(list(range(len(x_labels))))
        ax1.set_xticklabels([x_labels[i] for i in range(len(x_labels))], rotation=90)
        plt.ylabel(y_label)

        x_pos = range(len(x_labels))
        plt.bar(x_pos, y_values, align="center")

        ax1.set_yscale("symlog", linthreshy=1e-12)  # logarithmic plota

        plt.show()


class ActivitiesDataAnalysis(StatsAnalysis):
    """ Machine-learn activities data """

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

    def __init__(self, dataset_file):
        """
        :param dataset_file: str
            Path to folder with data to analyse
        """

        StatsAnalysis.__init__(self, dataset_file)

    def parse_csv(self):
        """
        :return: tuple [], [] of []
            Headers of csv file and data
        """

        headers, data = super(ActivitiesDataAnalysis, self).parse_csv()
        data = self.convert_time_columns(headers, self.TIME_HEADERS_TO_CONVERT, data)
        data = self.fix_floats(headers, self.HEADERS_WITH_MALFORMED_FLOATS, data)
        return headers, data

    def shows_correlation_matrix_of_data(self):
        """
        :return: void
            Shows correlation matrix of data of files in folder
        """

        self.show_correlation_matrix("Garmin activities data " + Document(self.dataset_file).name.strip(),
                                     self.HEADERS_TO_ANALYZE)
