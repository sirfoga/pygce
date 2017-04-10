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
from datetime import datetime

from models.bot import GarminConnectBot


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
    return parser


def parse_args(parser):
    """
    :param parser: ArgumentParser
        Object that holds cmd arguments.
    :return: tuple
        Values of arguments.
    """

    args = parser.parse_args()
    return str(args.user), str(args.password), str(args.path_chromedriver)


def main():
    user, password, chromedriver = parse_args(create_args())
    bot = GarminConnectBot(user, password, chromedriver)

    bot.go_to_day_summary(datetime(year=2017, month=3, day=29))
    print("got it!")


if __name__ == '__main__':
    main()
