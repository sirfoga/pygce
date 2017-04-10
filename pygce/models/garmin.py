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

        self.html = raw_html
        self.soup = BeautifulSoup(self.html)

    def parse(self):
        """
        :return: void
            Parses raw html source and tries to finds all information
        """


class GCDaySummary(GCDaySection):
    """
    Standard activity in the Garmin Connect timeline of day.
    Common features are day, likes, comment, kcal
    """

    def __init__(self, raw_html):
        """
        :param raw_html: str
            HTML source snippet with information about section
        """

        GCDaySection.__init__(self, raw_html)


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
