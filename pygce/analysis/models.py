# !/usr/bin/python3
# coding: utf-8


import matplotlib.pyplot as plt
import numpy as np
from hal.charts.bar import create_symlog_bar_chart, create_multiple_bar_chart
from hal.files.models import Document
from hal.ml.analysis import correlation
from hal.ml.data.parser import parse_csv_file
from hal.ml.utils import matrix as m_utils
from sklearn import linear_model, cluster, feature_selection

from pygce.models.garmin import utils


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
            if headers[
                i] in headers_to_convert:  # this columns id to be converted
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


class MLAnalysis(GarminDataFilter):
    """ Carries out popular machine-learning tasks on Garmin data """

    def __init__(self, dataset_file):
        """
        :param dataset_file: str
            Path to folder with data to analyse
        """

        GarminDataFilter.__init__(self, dataset_file)


class TimelineDataAnalysis(StatsAnalysis):
    """ Analyzes and provides insights into Garmin timeline data """

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
        "STEPS:goal"
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
        data = self.convert_time_columns(headers, self.TIME_HEADERS_TO_CONVERT,
                                         data)
        return headers, data

    def show_correlation_matrix_of_data(self):
        """
        :return: void
            Shows correlation matrix of data of files in folder
        """

        self.show_correlation_matrix(
            "Garmin timeline data " + Document(self.dataset_file).name.strip(),
            self.HEADERS_TO_ANALYZE)

    def predict_feature(self, feature):
        """
        :param feature: str
            Name of feature (column name) to predict
        :return: void
            Predicts feature with linear regression
        """

        print("Predicting ", feature, "with data from file", self.dataset_file)
        headers, raw_data = self.parse_csv()  # get columns names and raw data
        clf = linear_model.LinearRegression()  # model to fit data
        x_matrix_features = self.HEADERS_TO_ANALYZE.copy()
        x_matrix_features.remove(
            feature)  # do NOT include feature to predict in input matrix
        x_data = m_utils.get_subset_of_matrix(x_matrix_features, headers,
                                              raw_data)  # input matrix
        y_data = m_utils.get_subset_of_matrix([feature], headers,
                                              raw_data)  # output matrix
        clf.fit(x_data, y_data)

        coefficients = {}  # dict feature -> coefficient
        for i in range(len(x_matrix_features)):
            coefficients[x_matrix_features[i]] = clf.coef_[0][i]

        chart = create_symlog_bar_chart(
            "Linear fit of " + feature,
            [k for k in coefficients.keys()],
            coefficients.values(),
            "Coefficient"
        )
        plt.show()

    def cluster_analyze(self, n_clusters=6):
        """
        :param n_clusters: int
            Number of clusters
        :return: void
            Computes cluster analysis: see days based on differences.
            Each day is different from one another, there are days where you trained more, others where you ate more ...
            The goal is to divide your days into categories (e.g highly-active, active ...) based on data logs.
            This way, the input matrix consists of multiple vectors with each one consisting of one day's values.
        """

        print("Clustering file", self.dataset_file)
        headers, raw_data = self.parse_csv()  # get columns names and raw data
        x_data = m_utils.get_subset_of_matrix(self.HEADERS_TO_ANALYZE, headers,
                                              raw_data)  # input matrix
        kmeans = cluster.KMeans(n_clusters=n_clusters, random_state=0).fit(
            x_data)
        print("Clusters", kmeans.labels_)

        headers_to_plot = [
            "SUMMARY:kcal_count",
            "STEPS:distance",
            "SLEEP:deep_sleep_time",
            "ACTIVITIES:distance"
        ]  # get headers to add to chart
        vals_headers = [
            [float(row[headers.index(h)]) for row in raw_data] for h in
            headers_to_plot
        ]  # get values for each header
        headers_to_plot.append("cluster")  # add cluster group
        vals_headers.append(kmeans.labels_)
        days = [str(row[headers.index("date")]) for row in
                raw_data]  # get list of days (x values)

        chart = create_multiple_bar_chart(
            "Days",
            days,
            vals_headers,
            headers_to_plot
        )  # create chart
        plt.show()  # show bar chart

    def cluster_3d_plot(self, labels, n_clusters=6):
        """
        :param labels: [] of str (len = 3)
            Features to cluster data. Each item must be in the csv data file. Each label is one of x, y, z axis
        :param n_clusters: int
            Number of clusters
        :return: void
            Plots 3D chart with clusters based on selected features
        """

        print("Clustering file", self.dataset_file)
        headers, raw_data = self.parse_csv()  # get columns names and raw data
        x_data = m_utils.get_subset_of_matrix(self.HEADERS_TO_ANALYZE, headers,
                                              raw_data)  # input matrix
        kmeans = cluster.KMeans(n_clusters=n_clusters, random_state=0).fit(
            x_data)

        fig = plt.figure(figsize=(4, 3))  # create 3D plot
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(
            x_data[:, self.HEADERS_TO_ANALYZE.index(labels[0])],
            # get values of given labels
            x_data[:, self.HEADERS_TO_ANALYZE.index(labels[1])],
            x_data[:, self.HEADERS_TO_ANALYZE.index(labels[2])],
            c=kmeans.labels_.astype(np.float)
        )  # plot 3D data points

        centroids = kmeans.cluster_centers_
        cluster_centers = []  # list of centers of each cluster
        for i in range(n_clusters):
            cl_center = {
                "x": centroids[i][self.HEADERS_TO_ANALYZE.index(labels[0])],
                # x-coordinate of i-th cluster
                "y": centroids[i][self.HEADERS_TO_ANALYZE.index(labels[1])],
                # y-coordinate of i-th cluster
                "z": centroids[i][self.HEADERS_TO_ANALYZE.index(labels[2])]
                # z-coordinate of i-th cluster
            }  # x, y, z of center of first cluster -> find x, y, z of each label
            cluster_centers.append(cl_center)

        ax.scatter(
            [c["x"] for c in cluster_centers],
            # x positions of centers of all clusters
            [c["y"] for c in cluster_centers],
            # y positions of centers of all clusters
            [c["z"] for c in cluster_centers],
            # z positions of centers of all clusters
            marker='o',
            s=800,
            linewidth=5,
            color='w'
        )  # plot centroids

        ax.set_xlabel(labels[0])  # set labels
        ax.set_ylabel(labels[1])
        ax.set_zlabel(labels[2])

        plt.title(str(n_clusters) + "-clustering data")
        plt.show()

    def select_k_best(self, feature, k=5):
        """
        :param feature: str
            Name of feature (column name) to predict
        :param k: int
            Number of features to select
        :return: void
            Selects the best features to predict feature
        """

        print("Selecting k best features of data file", self.dataset_file)
        headers, raw_data = self.parse_csv()  # get columns names and raw data
        sel = feature_selection.SelectKBest(feature_selection.f_regression,
                                            k=k)  # model to select data
        x_matrix_features = self.HEADERS_TO_ANALYZE.copy()  # not edit main list of headers
        x_matrix_features.remove(
            feature)  # do NOT include feature to predict in input matrix
        x_data = m_utils.get_subset_of_matrix(x_matrix_features, headers,
                                              raw_data)  # input matrix
        y_data = m_utils.get_subset_of_matrix([feature], headers,
                                              raw_data)  # output matrix
        sel.fit(x_data, y_data)  # fit

        top_k_features_indices = np.array(sel.scores_).argsort()[-k:][
                                 ::-1]  # indices of top k features
        top_k_features = [x_matrix_features[i] for i in
                          top_k_features_indices]  # names of top k features
        top_k_features_scores = [sel.scores_[i] for i in
                                 top_k_features_indices]  # scores of top k features

        chart = create_symlog_bar_chart(
            "Most " + str(k) + " correlated features with " + feature,
            top_k_features,
            top_k_features_scores, "score")
        plt.show()


class ActivitiesDataAnalysis(StatsAnalysis):
    """ Analyzes and provides insights into Garmin activities data """

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
        data = self.convert_time_columns(headers, self.TIME_HEADERS_TO_CONVERT,
                                         data)
        data = self.fix_floats(headers, self.HEADERS_WITH_MALFORMED_FLOATS,
                               data)
        return headers, data

    def shows_correlation_matrix_of_data(self):
        """
        :return: void
            Shows correlation matrix of data of files in folder
        """

        self.show_correlation_matrix("Garmin activities data " + Document(
            self.dataset_file).name.strip(),
                                     self.HEADERS_TO_ANALYZE)
