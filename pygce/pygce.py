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

import argparse
import os
from datetime import datetime

from models.bot import GarminConnectBot


def parse_yyyy_mm_dd(d):
    """
    :param d: str
        Date in the form yyyy-mm-dd to parse
    :return: datetime
        Date parsed
    """

    d = str(d).strip()  # discard jibberish
    return datetime.strptime(d, "%Y-%m-%d")


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(
        usage="-u <username (email) to login to Garmin Connect> -p <password to login to Garmin Connect>")
    parser.add_argument("-u", dest="user", help="user to login to FSG website", required=True)
    parser.add_argument("-p", dest="password", help="password to login to FSG website", required=True)
    parser.add_argument("-c", dest="path_chromedriver", help="path to chromedriver to use", required=True)
    parser.add_argument("-d", nargs="*", dest="days",
                        help="days to save. e.g -d 2017-12-30 or -d 2016-01-01 2017-12-30", required=True)
    parser.add_argument("-o", dest="path_out", help="path to output file", required=True)
    return parser


def parse_args(parser):
    """
    :param parser: ArgumentParser
        Object that holds cmd arguments.
    :return: tuple
        Values of arguments.
    """

    args = parser.parse_args()

    raw_days = [str(d).strip() for d in args.days]  # parse days
    if len(raw_days) == 1:
        days = [parse_yyyy_mm_dd(raw_days[0]), parse_yyyy_mm_dd(raw_days[0])]
    else:
        days = [parse_yyyy_mm_dd(raw_days[0]), parse_yyyy_mm_dd(raw_days[1])]

    return str(args.user), str(args.password), str(args.path_chromedriver), days, str(args.path_out)


def check_args(user, password, chromedriver, days, path_out):
    """
    :param user: str
        User to use
    :param password: str
        Password to use
    :param chromedriver: str
        Path to chromedriver to use
    :param days: [] of datetime.date
        Days to save
    :param path_out: str
        File to use as output
    :return: bool
        True iff args are correct
    """

    assert (len(user) > 1)
    assert (len(password) > 1)
    assert (os.path.exists(chromedriver))
    assert (isinstance(days[0], datetime))
    assert (days[0] <= days[1])  # start day <= end day

    out_dir = os.path.dirname(path_out)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)  # create necessary dir for output file

    return True


def main():
    user, password, chromedriver, days, path_out = parse_args(create_args())
    if check_args(user, password, chromedriver, days, path_out):
        bot = GarminConnectBot(user, password, chromedriver)
        bot.save_json_days(days[0], days[1], path_out)
    else:
        print("Error while parsing args. Run 'pygce -h' for help")

if __name__ == '__main__':
    main()
