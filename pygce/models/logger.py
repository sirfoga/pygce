#!/usr/bin/env python3
# coding: utf-8


""" App logging tools """

import logging

# formatting
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


def log_message(*message):
    logger = get_logger()
    logger.debug(" ".join(message))


def log_error(exception, cause=None):
    logger = get_logger()
    text = str(exception)

    if cause:
        text += " because " + str(cause)

    logger.error(text)
