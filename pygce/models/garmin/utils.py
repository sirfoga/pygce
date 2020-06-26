# !/usr/bin/python3
# coding: utf-8
import json
from datetime import datetime

GARMIN_CONNECT_URL = "https://connect.garmin.com"
GARMIN_CONNECT_ACTIVITIES_URL = "https://connect.garmin.com/modern/activities"


def parse_num(n):
    """
    :param n: str
        Number to parse
    :return: float
        Parses numbers written like 123,949.99
    """

    m = str(n).strip().replace(".", "").replace(",", ".")
    return float(m)


def parse_hh_mm_ss(h):
    """
    :param h: str
        Hours, minutes and seconds in the form hh:mm:ss to parse
    :return: datetime.time
        Time parsed
    """

    h = str(h).strip()  # discard jibberish
    split_count = h.count(":")
    if split_count == 2:  # hh:mm:ss
        return datetime.strptime(str(h).strip(), "%H:%M:%S").time()
    elif split_count == 1:  # mm:ss
        return datetime.strptime(str(h).strip(), "%M:%S").time()
    else:  # ss
        return datetime.strptime(str(h).strip(), "%S").time()


def null_hh_mm_ss():
    """
    :return: datetime.time
        0 time parsed
    """

    return parse_hh_mm_ss("00:00:00")


def get_seconds(s):
    """
    :param s: str
        Datetime in the form %H:%M:%S
    :return: int
        Seconds in time
    """

    t = parse_hh_mm_ss(s)  # get time
    total_seconds = t.second
    total_seconds += t.minute * 60.0
    total_seconds += t.hour * 60.0 * 60.0
    return total_seconds


def parse_hh_mm(h):
    """
    :param h: str
        Hours and minutes in the form hh:mm to parse
    :return: datetime.time
        Time parsed
    """

    h = str(h).strip()  # discard jibberish
    split_count = h.count(":")
    if split_count == 1:  # hh:mm
        return datetime.strptime(str(h).strip(), "%H:%M").time()
    else:  # mm
        return datetime.strptime(str(h).strip(), "%M").time()


def json2pretty(data, output_file):
    with open(output_file, "w") as o:  # write to file
        json.dump(
            data, o, sort_keys=True, indent=4, separators=(',', ': ')
        )
