# !/usr/bin/python3
# coding: utf-8


import argparse
import os
from datetime import datetime

from pygce.models.bot import GarminConnectBot

AVAILABLE_OUTPUT_FORMATS = ["json", "csv"]


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
        usage="-u <username (email) to login to Garmin Connect> -p <password "
              "to login to Garmin Connect> -c <path to "
              "chromedriver to use> -d <days to save. e.g -d 2017-12-30 or "
              "-d 2016-01-01 2017-12-30> -f <format of "
              "output file [json, csv]> -o <path to output file>")
    parser.add_argument("-user", dest="user",
                        help="username (email) to login to Garmin Connect",
                        required=True)
    parser.add_argument("-password", dest="password",
                        help="password to login to Garmin Connect",
                        required=True)
    parser.add_argument("-url", dest="url",
                        help="url to connect to (e.g "
                             "https://connect.garmin.com)",
                        default=GarminConnectBot.DEFAULT_BASE_URL,
                        required=False)
    parser.add_argument("-chrome", dest="path_chromedriver",
                        help="path to chromedriver to use", required=True)
    parser.add_argument("-d", nargs="*", dest="days",
                        help="days to save. e.g -d 2017-12-30 or -d "
                             "2016-01-01 2017-12-30",
                        required=True)
    parser.add_argument("-f", dest="format_out",
                        help="<format of output file [json, csv]>",
                        required=True)
    parser.add_argument("-gpx", dest="gpx_out",
                        help="download .gpx files too [y/n]",
                        default="n",
                        required=False)
    parser.add_argument("-out", dest="path_out", help="path to output file",
                        required=True)
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

    args.gpx_out = (args.gpx_out.startswith("y"))

    return str(args.user), str(args.password), str(args.url), str(
        args.path_chromedriver), days, str(args.format_out), args.gpx_out, str(
        args.path_out)


def check_args(user, password, url, chromedriver, days, format_out, path_out):
    """
    :param user: str
        User to use
    :param password: str
        Password to use
    :param url: str
        Url to connect to
    :param chromedriver: str
        Path to chromedriver to use
    :param days: [] of datetime.date
        Days to save
    :param format_out: str
        Format of output file (json, csv)
    :param path_out: str
        File to use as output
    :return: bool
        True iff args are correct
    """

    assert (len(user) > 1)
    assert (len(password) > 1)
    assert ("https" in url and "garmin" in url)
    assert (os.path.exists(chromedriver))
    assert (isinstance(days[0], datetime))
    assert (days[0] <= days[1])  # start day <= end day
    assert format_out in AVAILABLE_OUTPUT_FORMATS

    out_dir = os.path.dirname(path_out)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)  # create necessary dir for output file

    return True


def main():
    user, password, url, chromedriver, days, format_out, gpx_out, path_out = \
        parse_args(create_args())
    if check_args(user, password, url, chromedriver, days, format_out,
                  path_out):
        bot = GarminConnectBot(user, password, gpx_out, chromedriver, url=url)

        if format_out == "json":
            bot.save_json_days(days[0], days[1], path_out)
        elif format_out == "csv":
            bot.save_csv_days(days[0], days[1], path_out)
    else:
        print("Error while parsing args. Run 'pygce -h' for help")


if __name__ == '__main__':
    main()
