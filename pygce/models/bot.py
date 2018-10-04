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

from models.logger import log_error, log_message
from .garmin.timeline import GCDayTimeline


class GarminConnectBot(object):
    """ Navigate through Garmin Connect app via a bot """

    USER_PATH = "/modern/"
    DEFAULT_BASE_URL = "https://connect.garmin.com"
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
    BROWSER_WAIT_TIMEOUT_SECONDS = 2  # max seconds before url request is
    BROWSER_GENERAL_ERROR = "If the error persist, please open an issue."
    BROWSER_TIMEOUT_ERROR = "Cannot complete request (cannot find {}). I " \
                            "suggest setting a larger browser timeout page. " + \
                            BROWSER_GENERAL_ERROR

    def __init__(self, user_name, password, download_gpx, chromedriver_path,
                 url=DEFAULT_BASE_URL):
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
        self.base_url = url

        garmin_region = self.user_url.split("/")[2].split("connect.")[-1]
        log_message("Region:", garmin_region)

        self.login_url = \
            self.BASE_LOGIN_URL.replace("garmin.com", garmin_region)

    def _wait_for(self, locator, element, attempts=3):
        for i in range(attempts):
            log_message("attempt", str(i))

            try:
                WebDriverWait(
                    self.browser,
                    self.BROWSER_WAIT_TIMEOUT_SECONDS
                ).until(
                    EC.presence_of_element_located(
                        (locator, element)
                    )
                )  # wait until fully loaded
                self.browser.find_element(locator, element)

                log_message("found " + element)
                return True
            except:
                pass  # maybe next time

        log_message(self.BROWSER_TIMEOUT_ERROR.format(element))
        return False

    def _perform_login(self):
        self.browser.execute_script(
            "document.getElementById(\"" + self.LOGIN_BUTTON_ID + "\").click()"
        )  # click button to login
        self._wait_for(By.CLASS_NAME, "activity-tracking-disclaimer")

    def _go_to(self, url, locator=None, element=None):
        log_message("GET", url)
        self.browser.get(url)

        if locator and element:
            if not self._wait_for(locator, element):
                raise ValueError(url + " not fully loaded")

    def login(self):
        """
        :return: bool
            True iff correctly logged in
        """

        try:
            self._go_to(self.login_url)  # open login url
            SeleniumForm.fill_login_form(
                self.browser,
                self.user_name, self.USERNAME_FIELD_NAME,
                self.user_password, self.PASSWORD_FIELD_NAME
            )  # fill login form
            self._perform_login()
            self.user_logged_in = True
            return True  # if arrived here, everything is fine
        except Exception as e:
            log_error(e)
            self.user_logged_in = False
            return False  # something went wrong

    def _get_user_id(self):
        self.go_to_dashboard()
        soup = BeautifulSoup(self.browser.page_source,
                             "lxml")  # html parser
        widget = soup.find("div", {"class": "header-nav-item user-profile"})
        candidates = widget.a["href"].split("/")
        raw = candidates[-1]
        return str(raw).strip()

    def _find_user_id(self):
        """
        :return: void
            Retrieves user unique id and token
        """

        if self.user_id is None:
            self.user_id = self._get_user_id()

        if self.user_id is None:
            raise ValueError("Cannot find user ID!")

    def go_to_dashboard(self):
        """
        :return: void
            Navigates to user homepage
        """

        if not self.user_logged_in:
            self.login()

        self._go_to(self.user_url, By.CLASS_NAME, "widget-content")

    def _get_day_url(self, date_time):
        url = self.base_url + "/modern/daily-summary/{}/{}"
        day = date_time.strftime('%Y-%m-%d')
        return url.format(self.user_id, day)

    def go_to_day(self, date_time):
        """
        :param date_time: datetime
            Datetime object with date
        :return: void
            Navigates to daily summary of given date
        """

        self._find_user_id()
        url = self._get_day_url(date_time)
        self._go_to(url, By.CLASS_NAME, "comment-container")

    def get_day(self, date_time):
        """
        :param date_time: datetime
            Datetime object with date
        :return: GCDayTimline
            Data about day
        """

        log_message("Getting day", str(date_time))
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
            max_date_time - min_date_time
        ).days  # days from begin to end
        days = []  # output list

        for i in range(days_delta + 1):  # including last day
            day = min_date_time + timedelta(days=i)
            days.append(self.get_day(day))

        return days

    def parse_days(self, min_date_time, max_date_time):
        """
        :param min_date_time: datetime
            Datetime object with date, this is the date when to start downloading data
        :param max_date_time: datetime
            Datetime object with date, this is the date when to stop downloading data
        :return: []
            List of data about days
        """

        data = self.get_days(min_date_time, max_date_time)  # get raw data

        for d in data:
            log_message("Parsing day", str(d.date))
            d.parse()  # parse

        return data

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

        data = self.parse_days(min_date_time, max_date_time)

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

        data = self.parse_days(min_date_time, max_date_time)

        csv_data = [d.to_csv_dict() for d in data]  # get csv
        csv_headers = csv_data[0].keys()  # get headers for a sample dict
        with open(output_file, "w") as o:  # write to file
            dict_writer = csv.DictWriter(o, csv_headers)
            dict_writer.writeheader()
            dict_writer.writerows(csv_data)

        self.save_gpx(csv_data)

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
                    self._go_to(activity["gpx"])
                    log_message(
                        "Saved .gpx for", activity["name"], activity["time_day"]
                    )
