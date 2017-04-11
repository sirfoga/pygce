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


import json
from datetime import datetime

from bs4 import BeautifulSoup


def parse_num(n):
    """
    :param n: str
        Number to parse
    :return: float
        Parses numbers written like 123,949.99
    """

    m = str(n).strip().replace(".", "").replace(",", ".")
    return float(m)


def parse_hours_minutes(h):
    """
    :param h: str
        Hours and minutes in the form hh:mm to parse
    :return: datetime.time
        Time parsed
    """

    return datetime.strptime(str(h).strip(), "%H:%M").time()


class GCDaySection(object):
    """
    Standard section in the Garmin Connect timeline of day.
    """

    def __init__(self, raw_html):
        """
        :param raw_html: str
            HTML source snippet with information about section
        """

        object.__init__(self)

        self.html = str(raw_html)
        self.soup = BeautifulSoup(self.html, "html.parser")

    def parse(self):
        """
        :return: void
            Parses raw html source and tries to finds all information
        """

    def to_dict(self):
        """
        :return: dict
            Dictionary with keys (obj fields) and values (obj values)
        """

        return {}

    def to_json(self):
        """
        :return: json object
            A json representation of this object
        """

        d = self.to_dict()
        for k in d.keys():
            d[k] = str(d[k])  # convert to string to be json serializable

        return json.dumps(d)


class GCDaySummary(GCDaySection):
    """
    Standard activity in the Garmin Connect timeline of day.
    Common features are likes, comment, kcal
    """

    def __init__(self, raw_html):
        """
        :param raw_html: str
            HTML source snippet with information about section
        """

        GCDaySection.__init__(self, raw_html)

        self.likes = None
        self.comment = None
        self.kcal_count = None

    def parse(self):
        self.parse_likes()
        self.parse_comment()
        self.parse_kcal_count()

    def parse_likes(self):
        """
        :return: void
            Finds likes count and stores value
        """

        container = self.soup.find_all("div", {"class": "span4 page-navigation"})[0]
        container = container.find_all("span", {"class": "like js-like-count"})[0]
        likes = container.text.strip().split(" ")[0]
        self.likes = parse_num(likes)

    def parse_comment(self):
        """
        :return: void
            Finds comment value and stores value
        """

        container = self.soup.find_all("div", {"class": "note-container"})[0]
        container = container.find_all("textarea", {"id": "noteTextarea"})[0]
        comment = str(container.text).strip()
        self.comment = comment

    def parse_kcal_count(self):
        """
        :return: void
            Finds kcal value and stores value
        """

        container = self.soup.find_all("div", {"class": "span8 daily-summary-stats-placeholder"})[0]
        container = container.find_all("div", {"class": "row-fluid top-xl"})[0]
        kcal_count = container.find_all("div", {"class": "data-bit"})[0].text
        self.kcal_count = parse_num(kcal_count)

    def to_dict(self):
        return {
            "likes": self.likes,
            "comment": self.comment,
            "kcal_count": self.kcal_count
        }


class GCDaySteps(GCDaySection):
    """
    Standard activity in the Garmin Connect timeline of day.
    Common features are total, goal, distance, avg daily
    """

    def __init__(self, raw_html):
        """
        :param raw_html: str
            HTML source snippet with information about section
        """

        GCDaySection.__init__(self, raw_html)

        self.total = None
        self.goal = None
        self.avg = None
        self.distance = None

    def parse(self):
        self.parse_steps_count()
        self.parse_steps_stats()

    def parse_steps_count(self):
        """
        :return: void
            Parses HTML source and finds goal and daily steps
        """

        container = self.soup.find_all("div", {"class": "span4 text-center charts"})[0]

        total = container.find_all("div", {"class": "data-bit"})[0].text  # finds total steps
        self.total = parse_num(total)

        goal = container.find_all("div", {"class": "h5"})[0].text.strip().split(" ")[-1].strip()
        self.goal = parse_num(goal)

    def parse_steps_stats(self):
        """
        :return: void
            Parses HTML source and finds daily distance and avg daily steps
        """

        container = self.soup.find_all("div", {"class": "span8 daily-summary-stats-placeholder"})[0]
        container = container.find_all("div", {"class": "row-fluid top-xl"})[0]
        container = container.find_all("div", {"class": "data-bit"})

        self.distance = parse_num(container[1].text.split("km")[0])
        self.avg = parse_num(container[2].text)

    def to_dict(self):
        return {
            "total": self.total,
            "goal": self.goal,
            "avg": self.avg,
            "distance": self.distance
        }


class GCDaySleep(GCDaySection):
    """
    Standard activity in the Garmin Connect timeline of day.
    Common features are total, deep total, light total, awake total
    """

    def __init__(self, raw_html):
        """
        :param raw_html: str
            HTML source snippet with information about section
        """

        GCDaySection.__init__(self, raw_html)

        self.night_sleep_time = None
        self.nap_time = None
        self.total_sleep_time = None  # typically night_sleep + nap
        self.bed_time = None
        self.wake_time = None
        self.deep_sleep_time = None
        self.light_sleep_time = None
        self.awake_sleep_time = None  # time during night you were awake

    def parse(self):
        self.parse_sleep_totals()
        self.parse_bed_time()
        self.parse_sleep_times()

    def parse_sleep_totals(self):
        """
        :return: void
            Finds value of night/nap/total sleep times
        """

        container = self.soup.find_all("div", {"class": "equation centered"})[0]
        times = container.find_all("div", {"class": "data-bit"})
        times = [str(t.text).strip() for t in times]  # strip texts

        self.night_sleep_time = parse_hours_minutes(times[0])
        self.nap_time = parse_hours_minutes(times[1])
        self.total_sleep_time = parse_hours_minutes(times[2].split(" ")[0])

    def parse_bed_time(self):
        """
        :return: void
            Finds hour start/end sleep
        """

        times = self.soup.find_all("div", {"class": "time-inline-edit-placeholder"})
        times = [str(t.text).strip() for t in times]  # strip texts

        self.bed_time = datetime.strptime(times[0], "%I:%M %p").time()  # account for AM/PM
        self.wake_time = datetime.strptime(times[1], "%I:%M %p").time()  # account for AM/PM

    def parse_sleep_times(self):
        """
        :return: void
            Finds deep/light/awake sleep times
        """

        container = self.soup.find_all("div", {
            "class": "span4 text-center sleep-chart-secondary deep-sleep-circle-chart-placeholder"})[0]
        self.deep_sleep_time = parse_hours_minutes(container.find_all("span")[0].text.split("hrs")[0])

        container = self.soup.find_all("div", {
            "class": "span4 text-center sleep-chart-secondary light-sleep-circle-chart-placeholder"})[0]
        self.light_sleep_time = parse_hours_minutes(container.find_all("span")[0].text.split("hrs")[0])

        container = self.soup.find_all("div", {
            "class": "span4 text-center sleep-chart-secondary awake-circle-chart-placeholder"})[0]
        self.awake_sleep_time = parse_hours_minutes(container.find_all("span")[0].text.split("hrs")[0])

    def to_dict(self):
        return {
            "night_sleep_time": self.night_sleep_time,
            "nap_time": self.nap_time,
            "total_sleep_time": self.total_sleep_time,
            "bed_time": self.bed_time,
            "wake_time": self.wake_time,
            "deep_sleep_time": self.deep_sleep_time,
            "light_sleep_time": self.light_sleep_time,
            "awake_sleep_time": self.awake_sleep_time
        }


class GCDayActivities(GCDaySection):
    """
    Standard activity in the Garmin Connect timeline of day.
    Common features are kcal, time, distance, type, name, link
    """

    def __init__(self, raw_html):
        """
        :param raw_html: str
            HTML source snippet with information about section
        """

        GCDaySection.__init__(self, raw_html)


class GCDayBreakdown(GCDaySection):
    """
    Standard activity in the Garmin Connect timeline of day.
    Common features are highly active %, active %, sedentary %, sleep %
    """

    def __init__(self, raw_html):
        """
        :param raw_html: str
            HTML source snippet with information about section
        """

        GCDaySection.__init__(self, raw_html)

        self.highly_active = None
        self.active = None
        self.sedentary = None
        self.sleeping = None

    def parse(self):
        values = self.soup.find_all("tspan")
        values = [str(v.text).strip().replace("%", "") for v in values]  # remove jibberish

        self.highly_active = parse_num(values[0])
        self.active = parse_num(values[1])
        self.sedentary = parse_num(values[2])
        self.sleeping = parse_num(values[3])

    def to_dict(self):
        return {
            "highly_active": self.highly_active,
            "active": self.active,
            "sedentary": self.sedentary,
            "sleeping": self.sleeping
        }


class GCDayTimeline(object):
    """
    Standard Garmin Connect timeline of day as in webpage.
    Each standard day consists of different sections:
    - summary (day, likes, comment, kcal)
    - steps (total, goal, distance, avg daily)
    - sleep (total, deep total, light total, awake total)
    - activities (for each one: kcal, time, distance, type, name, link)
    - breakdown (highly active %, active %, sedentary %, sleep %)
    """

    def __init__(self, date_time, summary_html, steps_section_html, sleep_section_html, activities_section_html,
                 breakdown_section_html):
        """
        :param date_time: datetime
            Datetime of day
        :param summary_html: str
            HTML source snippet with information about the day
        :param steps_section_html: str
            HTML source snippet with information about daily steps
        :param sleep_section_html: str
            HTML source snippet with information about daily sleep
        :param activities_section_html: str
            HTML source snippet with information about daily activities
        :param breakdown_section_html: str
            HTML source snippet with information about daily breakdown
        """

        object.__init__(self)

        self.date = date_time.date()
        self.sections = {
            "summary": GCDaySummary(summary_html),
            "steps": GCDaySteps(steps_section_html),
            "sleep": GCDaySleep(sleep_section_html),
            "activities": GCDayActivities(activities_section_html),
            "breakdown": GCDayBreakdown(breakdown_section_html)
        }  # list of sections in day

    def parse(self):
        """
        :return: void
            Finds all sections to parse, then builds corresponding objects and parses everything
        """

        for section in self.sections.values():  # parse each section
            section.parse()

    def __getattr__(self, item):
        return self.sections[item]
