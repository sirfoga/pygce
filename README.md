# PyGCE

*A tool to export your data from Garmin Connect, written in Python 3.*


## Install
```
$ pip3 install . --upgrade --force-reinstall
```
*To install from source, planned a pip-package for the future*


## Usage
```
usage: -u <username (email) to login to Garmin Connect> -p <password to login to Garmin Connect> -c <path to chromedriver to use> -d <days to fetch> -o <output file>

optional arguments:
  -h, --help            show this help message and exit
  -u USER               user to login to FSG website
  -p PASSWORD           password to login to FSG website
  -c PATH_CHROMEDRIVER  path to chromedriver to use
  -d [DAYS [DAYS ...]]  days to save. e.g -d 2017-12-30 or -d 2016-01-01
                        2017-12-30
  -o PATH_OUT           path to output file 
```


## Sample output
You can browse the [`json output`](sample.json) for a single day.

## Questions and issues
The [github issue tracker](https://github.com/sirfoga/pygce/issues) is **only** for bug reports and feature requests. Anything else, such as questions for help in using the library, should be posted as [pull requests](https://github.com/sirfoga/pygce/pulls)


## Thanks
Thanks to Garmin Connect for creating a semi-complete product: what if you've added an `EXPORT ALL DATA` button right at the bottom of the web-page? Would have hurt anybody?


## License
[Apache License](http://www.apache.org/licenses/LICENSE-2.0) Version 2.0, January 2004
