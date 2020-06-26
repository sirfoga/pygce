# !/usr/bin/python3
# coding: utf-8


import abc
import json
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from pygce.models.garmin import utils


class GCDaySection:
    """
    Standard section in the Garmin Connect timeline of day.
    """

    def __init__(self, raw_html, tag=""):
        """
        :param raw_html: str
            HTML source snippet with information about section
        :param tag: str
            Unique str in order not to mistake this GCDaySection with another one
        """

        self.tag = tag  # unique key in order not to mistake this GCDaySection with another one
        self.html = str(raw_html)
        self.soup = BeautifulSoup(self.html, "html.parser")

    @abc.abstractmethod
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

    def to_csv_dict(self):
        """
        :return: {}
            Like self.to_json() but with a unique str before each key to spot against different GCDaySections
        """

        d = self.to_dict()
        csv_d = {}
        for k in d.keys():
            new_key = str(self.tag) + ":" + k
            csv_d[new_key] = str(d[k])  # edit key
        return csv_d


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

        super().__init__(raw_html, tag="SUMMARY")

        self.likes = None
        self.comment = None
        self.kcal_count = None

    def parse(self):
        try:
            self.parse_likes()
        except:
            pass

        try:
            self.parse_comment()
        except:
            pass

        try:
            self.parse_kcal_count()
        except:
            pass

    def parse_likes(self):
        """
        :return: void
            Finds likes count and stores value
        """

        container = \
            self.soup.find_all("div", {"class": "span4 page-navigation"})[0]
        container = \
            container.find_all("span", {"class": "like js-like-count"})[0]
        likes = container.text.strip().split(" ")[0]
        self.likes = utils.parse_num(likes)

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

        container = self.soup.find_all("div", {
            "class": "span8 daily-summary-stats-placeholder"})[0]
        container = container.find_all("div", {"class": "row-fluid top-xl"})[0]
        kcal_count = container.find_all("div", {"class": "data-bit"})[0].text
        self.kcal_count = utils.parse_num(kcal_count)

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

        super().__init__(raw_html, tag="STEPS")

        self.total = None
        self.goal = None
        self.avg = None
        self.distance = None

    def parse(self):
        try:
            self.parse_steps_count()
        except:
            pass

        try:
            self.parse_steps_stats()
        except:
            pass

    def parse_steps_count(self):
        """
        :return: void
            Parses HTML source and finds goal and daily steps
        """

        container = \
            self.soup.find_all("div", {"class": "span4 text-center charts"})[0]

        total = container.find_all("div", {"class": "data-bit"})[
            0].text  # finds total steps
        self.total = utils.parse_num(total)

        goal = \
            container.find_all("div", {"class": "h5"})[0].text.strip().split(
                " ")[
                -1].strip()
        self.goal = utils.parse_num(goal)

    def parse_steps_stats(self):
        """
        :return: void
            Parses HTML source and finds daily distance and avg daily steps
        """

        container = self.soup.find_all("div", {
            "class": "span8 daily-summary-stats-placeholder"})[0]
        container = container.find_all("div", {"class": "row-fluid top-xl"})[0]
        container = container.find_all("div", {"class": "data-bit"})

        self.distance = utils.parse_num(container[1].text.split("km")[0])
        self.avg = utils.parse_num(container[2].text)

    def to_dict(self):
        return {
            "total": self.total,
            "goal": self.goal,
            "avg": self.avg,
            "distance": self.distance
        }


class GCDetailsSteps(GCDaySection):
    """Steps divided into 15-minute bins"""

    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
    OUT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, date_time, raw_html):
        super().__init__(raw_html, tag="STEPS DETAILS")

        self.date_time = date_time
        self.content = json.loads(self.html)
        self.bins = []

    @staticmethod
    def parse_steps_count(raw):
        raw = str(raw)
        if raw.endswith('.0'):  # remove decimal point
            raw = raw[:-2]

        raw = raw.replace('.', '')  # remove thousands point

        return int(raw)

    def parse(self):
        for data in self.content:
            date_time = data['startGMT'][:-2]  # remove trailing 0
            date_time = datetime.strptime(date_time, self.DATE_FORMAT)

            date_time = date_time.strftime(self.OUT_DATE_FORMAT)
            steps_count = int(data['steps'])

            self.bins.append({
                'time': date_time,
                'steps': self.parse_steps_count(steps_count)
            })

    def to_dict(self):
        return {
            '15-min bins': self.bins
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

        super().__init__(raw_html, tag="SLEEP")

        self.night_sleep_time = None
        self.nap_time = None
        self.total_sleep_time = None  # typically night_sleep + nap
        self.bed_time = None
        self.wake_time = None
        self.deep_sleep_time = None
        self.light_sleep_time = None
        self.awake_sleep_time = None  # time during night you were awake

    def parse(self):
        try:
            self.parse_sleep_totals()
        except:
            pass

        try:
            self.parse_bed_time()
        except:
            pass

        try:
            self.parse_sleep_times()
        except:
            pass

    def parse_sleep_totals(self):
        """
        :return: void
            Finds value of night/nap/total sleep times
        """

        container = \
            self.soup.find_all("div", {"class": "equation centered"})[0]
        times = container.find_all("div", {"class": "data-bit"})
        times = [str(t.text).strip() for t in times]  # strip texts
        self.night_sleep_time = utils.parse_hh_mm(times[0])
        self.nap_time = utils.parse_hh_mm(times[1])
        self.total_sleep_time = utils.parse_hh_mm(times[2].split(" ")[0])

    def parse_bed_time(self):
        """
        :return: void
            Finds hour start/end sleep
        """

        times = self.soup.find_all(
            "div", {"class": "time-inline-edit-placeholder"}
        )
        times = [str(t.text).strip() for t in times]  # strip texts
        self.bed_time = datetime.strptime(
            times[0], "%I:%M %p").time()  # account for AM/PM
        self.wake_time = datetime.strptime(
            times[1], "%I:%M %p").time()  # account for AM/PM

    def parse_sleep_times(self):
        """
        :return: void
            Finds deep/light/awake sleep times
        """

        base_class = "span4 text-center sleep-chart-secondary"
        container = self.soup.find_all("div", {
            "class": base_class + " deep-sleep-circle-chart-placeholder"})[
            0]
        self.deep_sleep_time = utils.parse_hh_mm(
            container.find_all("span")[0].text.split("hrs")[0])

        container = self.soup.find_all("div", {
            "class": base_class + " light-sleep-circle-chart-placeholder"})[
            0]
        self.light_sleep_time = utils.parse_hh_mm(
            container.find_all("span")[0].text.split("hrs")[0])

        container = self.soup.find_all("div", {
            "class": base_class + " awake-circle-chart-placeholder"})[
            0]
        self.awake_sleep_time = utils.parse_hh_mm(
            container.find_all("span")[0].text.split("hrs")[0])

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

    GPX_DOWNLOAD_URL = "https://connect.garmin.com/modern/proxy/download-service/export/gpx/activity/"

    def __init__(self, raw_html):
        """
        :param raw_html: str
            HTML source snippet with information about section
        """

        super().__init__(raw_html, tag="ACTIVITIES")
        self.activities = []

    def parse(self):
        rows = self.soup.find_all("tr")
        for r in rows[1:]:  # discard header
            try:
                activity = self.parse_activity(r)
                self.activities.append(activity)
            except:
                pass

    @staticmethod
    def parse_activity(raw_html):
        """
        :param raw_html: str html code
            Raw HTML code of row of table containing activity to parse
        :return: dict
            Dict with values of activity
        """

        columns = raw_html.find_all("td")

        time_day = columns[0].text.strip()  # parse time of the day
        try:
            time_day = datetime.strptime(columns[0].text.strip(),
                                         "%I:%M %p").time()  # account for AM/PM
        except:
            pass

        try:
            duration = utils.parse_hh_mm_ss(
                columns[2].text.strip())  # in case of multiple hours
        except:
            duration = utils.parse_hh_mm_ss("00:00")

        link = str(columns[5].a["href"]).strip()
        id_ref = link.split("/")[-1]

        try:
            url = utils.GARMIN_CONNECT_URL + link
        except:
            url = None

        return {
            "time_day": time_day,
            "kcal": utils.parse_num(columns[1].text),
            "duration": duration,
            "distance": utils.parse_num(columns[3].text.split("km")[0]),
            "type": columns[4].text.strip(),
            "name": columns[5].text.strip(),
            "url": url,
            "gpx": GCDayActivities.GPX_DOWNLOAD_URL + id_ref
        }

    def to_dict(self):
        return {
            "activities": self.activities
        }

    def to_json(self):
        activities = self.activities
        for a in activities:
            for k in a.keys():
                a[k] = str(a[k])  # convert each field to string

        return json.dumps(activities)

    def to_csv_dict(self):
        """
        :return: {}
            Like super.to_csv_dict() but with totals instead
        """

        d = self.get_totals_dict()
        csv_d = {}
        for k in d.keys():
            new_key = str(self.tag) + ":" + k
            csv_d[new_key] = str(d[k])  # edit key
        return csv_d

    def get_total_kcal(self):
        """
        :return: float
            Total kcal of all activities
        """

        return sum(a["kcal"] for a in self.activities)

    def get_total_duration(self):
        """
        :return: timedelta
            Total duration of all activities
        """

        all_durations = [a["duration"] for a in
                         self.activities]  # fetch duration of all activities
        total_duration = timedelta(hours=0, minutes=0, seconds=0)
        for duration in all_durations:
            total_duration += timedelta(hours=duration.hour,
                                        minutes=duration.minute,
                                        seconds=duration.second)  # sum all durations
        return total_duration

    def get_total_distance(self):
        """
        :return: float
            Total distance of all activities
        """

        return sum(a["distance"] for a in self.activities)

    def get_totals_dict(self):
        """
        :return: {}
            Self dict but with totals instead (total kcal, total distance ...)
        """

        return {
            "kcal": self.get_total_kcal(),
            "duration": str(self.get_total_duration()),
            "distance": self.get_total_distance(),
        }


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

        super().__init__(raw_html, tag="BREAKDOWN")

        self.highly_active = None
        self.active = None
        self.sedentary = None
        self.sleeping = None

    def parse(self):
        values = self.soup.find_all("tspan")
        values = [str(v.text).strip().replace("%", "") for v in
                  values]  # remove jibberish

        try:
            self.highly_active = utils.parse_num(values[0])
        except:
            pass  # None

        try:
            self.active = utils.parse_num(values[1])
        except:
            pass  # None

        try:
            self.sedentary = utils.parse_num(values[2])
        except:
            pass  # None

        try:
            self.sleeping = utils.parse_num(values[3])
        except:
            pass  # None

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

    def __init__(self, date_time, summary_html,
                 steps_section_html, steps_details_html,
                 sleep_section_html, activities_section_html,
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
            "steps details": GCDetailsSteps(date_time, steps_details_html),
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

    def to_dict(self):
        """
        :return: dict
            Dictionary with keys (obj fields) and values (obj values)
        """

        return self.sections

    def to_csv_dict(self):
        """
        :return: {}
            Like self.to_dict() but with a set with keys and values NOT nested. Also for activities there are totals only
        """

        d = {
            "date": str(self.date)
        }  # resulting dict
        for section in self.sections.values():
            d.update(section.to_csv_dict())  # add each section keys

        return d

    def to_json(self):
        """
        :return: json object
            A json representation of this object
        """

        sections_dumps = {}  # dict section name -> section json
        for s in self.sections.keys():
            sections_dumps[s] = json.loads(
                self.sections[s].to_json())  # json object

        day_dump = {
            str(self.date): sections_dumps  # add date
        }

        return json.dumps(day_dump)
