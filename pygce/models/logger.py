#!/usr/bin/env python3
# coding: utf-8


""" App logging tools """

import logging
import threading

# formatting
LOG_THREAD_FORMAT = "thread-{} {} {}"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

LOG_LEVEL = logging.DEBUG

LOGGER = logging.getLogger("pygce")
LOGGER.setLevel(LOG_LEVEL)

STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setLevel(LOG_LEVEL)
STREAM_HANDLER.setFormatter(logging.Formatter(LOG_FORMAT))

LOGGER.addHandler(STREAM_HANDLER)


def get_logger():
    return LOGGER


def log_message(message):
    logger = get_logger()
    logger.debug(message)


def log_error(race, cause=None):
    logger = get_logger()
    thread_id = threading.current_thread().ident
    text = race.text + " " + race.year
    if cause:
        text += " because " + str(cause)

    logger.error(LOG_THREAD_FORMAT.format(thread_id, text, race.url))
