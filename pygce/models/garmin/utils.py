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


from datetime import datetime

GARMIN_CONNECT_URL = "https://connect.garmin.com"


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
