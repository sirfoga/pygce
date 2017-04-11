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

from bs4 import BeautifulSoup


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

        return json.dumps(self.to_dict())


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
        likes = container.text.strip().split(" ")[0].strip()
        likes = int(likes)
        self.likes = likes

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
        kcal_count = str(kcal_count).strip().replace(".", "")  # remove trailing digit
        kcal_count = int(kcal_count)
        self.kcal_count = kcal_count

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


class GCDayActivity(GCDaySection):
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
            "activities": GCDayActivity(activities_section_html),
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
