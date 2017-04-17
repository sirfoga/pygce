# PyGCE

*A tool to export, save, and analyze your Garmin Connect data*

[![PyPI version](https://badge.fury.io/py/pygce.svg)](https://pypi.python.org/pypi/pygce) [![Code Health](https://landscape.io/github/sirfoga/pygce/master/landscape.svg?style=flat
)](https://landscape.io/github/sirfoga/pygce/master)

There is a [detailed blog post](https://sirfoga.github.io/2017/04/16/pygce) explaining all this fuss in a nice and easy way. Please, take a look.

## Install
```
$ pip3 install . --upgrade --force-reinstall
```
*To install from source, planned a pip-package for the future*


## Usage
A simple `pygce -h` from the terminal should result in this output
```
usage: -u <username (email) to login to Garmin Connect> -p <password to login to Garmin Connect> -c <path to chromedriver to use> -d <days to save. e.g -d 2017-12-30 or -d 2016-01-01 2017-12-30> -f <format of output file [json, csv]> -o <path to output file>

optional arguments:
  -h, --help            show this help message and exit
  -u USER               username (email) to login to Garmin Connect
  -p PASSWORD           password to login to Garmin Connect
  -c PATH_CHROMEDRIVER  path to chromedriver to use
  -d [DAYS [DAYS ...]]  days to save. e.g -d 2017-12-30 or -d 2016-01-01
                        2017-12-30
  -f FORMAT_OUT         <format of output file [json, csv]>
  -o PATH_OUT           path to output file
```
When called with appropriate args `pygce` saves `.csv` or `.json` data dumps of your Garmin Connect timeline data. The files will look like
```
{
  "2017-04-09": {
    "steps": {
      "avg": "12948.0",
      "goal": "11197.0",
      "distance": "19.7",
      "total": "16902.0"
    },
    "sleep": {
      "total_sleep_time": "00:08:23",
      "light_sleep_time": "00:03:16",
      "awake_sleep_time": "00:00:19",
      "deep_sleep_time": "00:04:48",
      "wake_time": "07:34:00",
      "bed_time": "23:11:00",
      "nap_time": "00:00:00",
      "night_sleep_time": "00:08:23"
    },
    "activities": [
```
You can browse a [`full json output`](sample.json) for a single day.
If you instead chose the `csv` output format you should see something like this:
```
SUMMARY:comment,SLEEP:deep_sleep_time,ACTIVITIES:distance,STEPS:goal,STEPS:distance,BREAKDOWN:sleeping,SUMMARY:likes,SLEEP:bed_time,STEPS:avg,SLEEP:light_sleep_time
sweet dinner,00:04:55,22.82,10000,22.8,29,6,22:22:00,12087,00:03:36
met girlfriend in river park,00:02:47,8.92,10200,8.9,22,9,01:05:00,11940,00:01:42
droven all around ny,00:03:41,3.38,10272,3.4,27,2,03:01:00,10045,00:02:33
```
Browse a [`sample csv output`](sample.csv) for 3 days.


## Documentation
- You can browse the [html](docs/doxygen/html/index.html) (or if you prefer the [epydoc docs](docs/epydoc/html/index.html))
- There is also the [pdf](docs/doxygen/latex/refman.pdf) version (for the epydoc pdfs go [here](docs/epydoc/pdf/api.pdf))


## Questions and issues
The one thing to note is that you should have a [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) downloaded locally: when `pygce` runs, it opens a `Google Chrome` window and starts navigating through your Garmin Connect timeline, saving the results.

The [github issue tracker](https://github.com/sirfoga/pygce/issues) is **only** for bug reports and feature requests. Anything else, such as questions for help in using the library, should be posted as [pull requests](https://github.com/sirfoga/pygce/pulls).


## Thanks
Thanks to Garmin Connect for creating a semi-complete product: what if you've added an `EXPORT ALL DATA` button right at the bottom of the web-page? Would have hurt anybody?


## License
[Apache License](http://www.apache.org/licenses/LICENSE-2.0) Version 2.0, January 2004
