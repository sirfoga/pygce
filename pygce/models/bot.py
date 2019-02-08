# !/usr/bin/python3
# coding: utf-8


import csv
import json
import os
from datetime import timedelta
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from hal.internet.selenium.forms import SeleniumFormFiller
from hal.internet.utils import add_params_to_url
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from models.garmin.utils import json2pretty
from pygce.models.garmin.timeline import GCDayTimeline
from pygce.models.logger import log_error, log_message


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
    STEPS_DETAILS_PATH = '/modern/proxy/wellness-service/wellness' \
                         '/dailySummaryChart/'
    DATE_FORMAT = '%Y-%m-%d'
    LOGIN_BUTTON_ID = "login-btn-signin"  # html id of the login button
    USERNAME_FIELD_NAME = "username"  # html name of username in login form
    PASSWORD_FIELD_NAME = "password"  # html name of password in login form
    BROWSER_WAIT_TIMEOUT_SECONDS = 3  # max seconds before url request is
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
            SeleniumFormFiller(self.browser).fill_login_form(
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

    def get_html_parser(self, page_format="html.parser"):
        return BeautifulSoup(str(self.browser.page_source), page_format)

    def _get_user_id(self):
        self.go_to_dashboard()
        soup = self.get_html_parser("lxml")
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
        day = date_time.strftime(self.DATE_FORMAT)
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

    def _get_steps_details_url(self, date_time):
        url = urljoin(self.base_url, self.STEPS_DETAILS_PATH)
        url = urljoin(url, self.user_id)

        params = {'date': date_time.strftime(self.DATE_FORMAT)}
        url = add_params_to_url(url, params)
        return url

    def go_to_steps_details(self, date_time):
        self._find_user_id()
        url = self._get_steps_details_url(date_time)
        self._go_to(url, By.TAG_NAME, "pre")

    def get_steps_details(self, date_time):
        try:
            self.go_to_steps_details(date_time)
            soup = self.get_html_parser()
            steps_details_html = soup.find('pre').text
            log_message("found steps details data")
        except:
            steps_details_html = '[]'
            log_message("NOT found steps details data")

        return steps_details_html

    def get_day(self, date_time):
        """
        :param date_time: datetime
            Datetime object with date
        :return: GCDayTimline
            Data about day
        """

        log_message("Getting day", str(date_time))
        self.go_to_day(date_time)
        soup = self.get_html_parser()

        tabs_html = soup.find("div", {"class": "tab-content"})
        summary_html = soup.find("div", {
            "class": "content page steps sleep calories timeline"})
        steps_html = soup.find("div", {"class": "row-fluid bottom-m"})

        try:
            sleep_html = tabs_html.find("div", {"id": "pane5"})
            log_message("found sleep data")
        except:
            sleep_html = None
            log_message("NOT found sleep data")

        try:
            activities_html = tabs_html.find("div", {"id": "pane4"})
            log_message("found activities data")
        except:
            activities_html = None
            log_message("NOT found activities data")

        try:
            breakdown_html = tabs_html.find("div", {"id": "pane2"})
            log_message("found breakdown data")
        except:
            breakdown_html = None
            log_message("NOT found breakdown data")

        yesterday = date_time + timedelta(days=-1)
        today = date_time
        tomorrow = date_time + timedelta(days=1)

        steps_details_html_yesterday = json.loads(self.get_steps_details(
            yesterday
        ))
        steps_details_html_today = json.loads(self.get_steps_details(
            today
        ))
        steps_details_html_tomorrow = json.loads(self.get_steps_details(
            tomorrow
        ))

        steps_details_html = json.dumps(
            steps_details_html_yesterday +
            steps_details_html_today +
            steps_details_html_tomorrow
        )  # merge days

        return GCDayTimeline(
            date_time,
            summary_html,
            steps_html,
            steps_details_html,
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
            d.parse()  # parse

        return data

    @staticmethod
    def save_json_steps_details(data, output_folder):
        for d in data:
            steps_details = d.sections["steps details"].to_dict()
            output_file = 'step_details_' + str(d.date) + '.json'
            output_file = os.path.join(output_folder, output_file)

            json_data = steps_details
            json_data['date'] = str(d.date)

            json2pretty(json_data, output_file)

    @staticmethod
    def save_csv_steps_details(data, output_folder):
        for d in data:
            steps_details = d.sections["steps details"].to_dict()
            output_file = 'step_details_' + str(d.date) + '.csv'
            output_file = os.path.join(output_folder, output_file)

            steps_details = list(steps_details.values())[0]
            csv_headers = steps_details[0].keys()  # sample of keys
            with open(output_file, "w") as o:  # write to file
                dict_writer = csv.DictWriter(o, csv_headers)
                dict_writer.writeheader()

                dict_writer.writerows(steps_details)

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
        self.save_json_steps_details(data, os.path.dirname(output_file))
        for d in data:  # remove steps details
            del d.sections["steps details"]

        json_data = [json.loads(d.to_json()) for d in
                     data]  # convert to json objects
        json2pretty(json_data, output_file)

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
        self.save_csv_steps_details(data, os.path.dirname(output_file))
        for d in data:  # remove steps details
            del d.sections["steps details"]

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

    def close(self):
        self.browser.close()
