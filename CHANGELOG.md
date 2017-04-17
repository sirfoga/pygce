# Change Log
All notable changes to this project will be documented in this file.

# TODO
- GCDaySection.parse_json, GCDaySection.parse_csv
- test suite

## 0.1 - 2017-04-17

### Added
- cluster analyze
- show correlation matrix
- docs
- gitignore with latex
- analysis.cli

### Refactored
- analysis.models

## 0.0.9 - 2017-04-16

### Added
- ml linear regression analysis
- ml bar_chart

## 0.0.8 - 2017-04-15

### Refactored
- analysis script

## 0.0.7 - 2017-04-13

### Added
- CorrelationAnalysis
- garmin.activity models
- activities analysis

### Refactored
- split GCDayTimeline in garmin.timeline and garmin.utils packages

## 0.0.6 - 2017-04-12

### Added
- sample csv
- csv guidelines in README
- GCDaySection.to_csv_dict()
- GCDayTimeline.to_csv_dict()
- verbose mode when getting days data

### Fixed
- parse sleep times

## 0.0.5 - 2017-04-12

### Added
- csv cmd arg
- usage example and output example in 
- GCDayActivities.get_totals
- GCDaySection.tag

### Fixed
- help in cmd args
- GCDayActivities.get_totals

## 0.0.4 - 2017-04-12

### Added
- cmd args
- sample usage in README

### Fixed
- setup script

## 0.0.3 - 2017-04-11

### Added
- GCDaySummary, GCDaySteps, GCDaySleep, GCDayBreakdown converters and parsers
- GCDayTimeline to json
- .json sample output of day data
- .json days batch

## 0.0.2 - 2017-04-10

### Added
- GarminConnectBot to login, goto daily summary and dashboard of user, get daily data
- sample use of bot
- GCDayTimeline

## 0.0.1 - 2017-04-10

### Added
- `setup.py`, README
- garmin models

### Created
- repository
