# !/usr/bin/python3
# coding: utf-8


import csv
import json
from datetime import timedelta

from bs4 import BeautifulSoup
from hal.internet.selenium_bots import SeleniumForm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .garmin.timeline import GCDayTimeline


class GarminConnectBot(object):
    """ Navigate through Garmin Connect app via a bot """

    USER_PATH = "/modern/"
    BASE_URL = "https://connect.garmin.com"
    BASE_LOGIN_URL = "https://sso.garmin.com/sso/login?service=https%3A%2F" \
                     "%2Fconnect.garmin.com" \
                     "%2Fmodern%2F&webhost=olaxpw" \
                     "-conctmodern005.garmin.com&source=https%3A%2F%2Fconnect.garmin.com%2Fen-US%2Fsignin" \
                "&redirectAfterAccountLoginUrl=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F" \
                "&redirectAfterAccountCreationUrl=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&gauthHost=https%3A%2F" \
                "%2Fsso.garmin.com%2Fsso&locale=en_US&id=gauth-widget&clientId=GarminConnect&initialFocus=true" \
                "&embedWidget=false&mobile=false# "
    LOGIN_BUTTON_ID = "login-btn-signin"  # html id of the login button
    USERNAME_FIELD_NAME = "username"  # html name of username in login form
    PASSWORD_FIELD_NAME = "password"  # html name of password in login form
    BROWSER_WAIT_TIMEOUT_SECONDS = 25  # max seconds before url request is

    # discarded

    def __init__(self, user_name, password, download_gpx, chromedriver_path,
                 url=BASE_URL):
        """
        :param user_name: str
            Username (email) to login to Garmin Connect
        :param password: str
            Password to login to Garmin Connect
        :param download_gpx: bool
            Download .gpx files of activities
        :param chromedriver_path: str
            Path to Chrome driver to use as browser
        :param url: str
            Url to base downloads on
        """

        object.__init__(self)

        self.browser = webdriver.Chrome(
            chromedriver_path)  # bot browser to use
        self.user_name = user_name  # user settings
        self.user_password = password
        self.user_logged_in = False  # True iff user is correctly logged in
        self.user_id = None  # id of user logged in
        self.download_gpx = download_gpx
        self.user_url = url + self.USER_PATH
        garmin_region = self.user_url.split("/")[2].split("connect.")[-1]
        log_message(garmin_region)

        self.login_url = \
            self.BASE_LOGIN_URL.replace("garmin.com", garmin_region)

    def login(self):
        """
        :return: bool
            True iff correctly logged in
        """

        try:
            self.browser.get(self.login_url)  # open login url
            SeleniumForm.fill_login_form(
                self.browser,
                self.user_name, self.USERNAME_FIELD_NAME,
                self.user_password, self.PASSWORD_FIELD_NAME
            )  # fill login form
            self.browser.execute_script(
                "document.getElementById(\"" + self.LOGIN_BUTTON_ID + "\").click()")  # click button to login
            WebDriverWait(self.browser,
                          self.BROWSER_WAIT_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "activity-tracking-disclaimer"))
            )  # wait until fully loaded

            self.user_logged_in = True
            return True  # if arrived here, everything is fine
        except Exception as e:
            print(str(e))
            self.user_logged_in = False
            return False  # something went wrong

    def _find_user_id(self):
        """
        :return: void
            Retrieves user unique id and token
        """

        if not self.user_id:
            self.go_to_dashboard()
            soup = BeautifulSoup(self.browser.page_source,
                                 "lxml")  # html parser
            widgets = soup.find_all("div", {"class": "widget-content"})

            id_found = False  # True iff id has been found
            for w in widgets:
                if not id_found:
                    try:
                        widget_title = w.find_all("h3", {"class": "data-bit"})[
                            0]
                        raw_id = widget_title.a["href"]
                        tokens = raw_id.split("/")
                        candidate_id = max(tokens,
                                           key=len)  # longest string (typically is the id, since it's 36 chars)
                        self.user_id = str(candidate_id).strip()
                        id_found = True
                    except:
                        pass  # that widget didn't contain the id .. skip to the next

    def go_to_dashboard(self):
        """
        :return: void
            Navigates to user homepage
        """

        if not self.user_logged_in:
            self.login()

        print("Getting user dashboard from", self.user_url)
        self.browser.get(self.user_url)
        WebDriverWait(self.browser, self.BROWSER_WAIT_TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.CLASS_NAME, "widget-content"))
        )  # wait until fully loaded

    def go_to_day(self, date_time):
        """
        :param date_time: datetime
            Datetime object with date
        :return: void
            Navigates to daily summary of given date
        """

        self._find_user_id()
        date_to_to = date_time.strftime(
            '%Y-%m-%d')  # retrieve year, month and day to to go to
        url_to_get = "https://connect.garmin.com/modern/daily-summary/" + str(
            self.user_id) + "/" + date_to_to
        self.browser.get(url_to_get)
        WebDriverWait(self.browser, self.BROWSER_WAIT_TIMEOUT_SECONDS).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "comment-container"))
        )  # wait until fully loaded

    def get_day(self, date_time):
        """
        :param date_time: datetime
            Datetime object with date
        :return: GCDayTimline
            Data about day
        """

        try:
            print("Getting day", str(date_time))
            self.go_to_day(date_time)
            soup = BeautifulSoup(str(self.browser.page_source),
                                 "html.parser")  # html parser

            tabs_html = soup.find_all("div", {"class": "tab-content"})[
                0]  # find html source code for sections
            summary_html = soup.find_all("div", {
                "class": "content page steps sleep calories timeline"})[0]
            steps_html = soup.find_all("div", {"class": "row-fluid bottom-m"})[
                0]
            sleep_html = tabs_html.find_all("div", {"id": "pane5"})[0]
            activities_html = tabs_html.find_all("div", {"id": "pane4"})[0]
            breakdown_html = tabs_html.find_all("div", {"id": "pane2"})[0]

            return GCDayTimeline(
                date_time,
                summary_html,
                steps_html,
                sleep_html,
                activities_html,
                breakdown_html
            )
        except Exception as e:
            print(str(e))
            return None

    def get_days(self, min_date_time, max_date_time):
        """
        :param min_date_time: datetime
            Datetime object with date, this is the date when to start downloading data
        :param max_date_time: datetime
            Datetime object with date, this is the date when to stop downloading data
        :return: [] of GCDayTimline
            List of data about days
        """

        days_delta = (
            max_date_time - min_date_time).days  # days from begin to end
        days_data = []  # output list
        for i in range(days_delta + 1):  # including last day
            day_to_get = min_date_time + timedelta(days=i)
            days_data.append(self.get_day(day_to_get))
        return days_data

    def save_json_days(self, min_date_time, max_date_time, output_file):
        """
        :param min_date_time: datetime
            Datetime object with date, this is the date when to start downloading data
        :param max_date_time: datetime
            Datetime object with date, this is the date when to stop downloading data
        :param output_file: str
            Path where to save output to
        :return: void
            Retrieves data about days in given range, then saves json dump
        """

        data = self.get_days(min_date_time, max_date_time)  # get raw data
        for d in data:
            print("Parsing day", str(d.date))
            d.parse()  # parse

        json_data = [json.loads(d.to_json()) for d in
                     data]  # convert to json objects
        with open(output_file, "w") as o:  # write to file
            json.dump(json_data, o)

        self.save_gpx(data)

    def save_csv_days(self, min_date_time, max_date_time, output_file):
        """
        :param min_date_time: datetime
            Datetime object with date, this is the date when to start downloading data
        :param max_date_time: datetime
            Datetime object with date, this is the date when to stop downloading data
        :param output_file: str
            Path where to save output to
        :return: void
            Retrieves data about days in given range, then saves csv dump
        """

        data = self.get_days(min_date_time, max_date_time)  # get raw data
        for d in data:
            print("Parsing day", str(d.date))
            d.parse()  # parse

        data = [d.to_csv_dict() for d in data]  # get csv
        csv_headers = data[0].keys()  # get headers for a sample dict
        with open(output_file, "w") as o:  # write to file
            dict_writer = csv.DictWriter(o, csv_headers)
            dict_writer.writeheader()
            dict_writer.writerows(data)

        self.save_gpx(data)

    def save_gpx(self, data):
        """
        :param data: [] of GCDayTimeline
            Timeline with activities
        :return: void
            Downloads .gpx file for each activity to folder
        """

        if self.download_gpx:
            timelines = [timeline.activities for timeline in data]
            for timeline in timelines:
                for activity in timeline.activities:
                    self.browser.get(activity["gpx"])
                    print("Saved .gpx for", activity["name"],
                          activity["time_day"])
