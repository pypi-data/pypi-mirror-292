#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import logging

fragment_logger = logging.getLogger("fragment")
async_collie_logger = logging.getLogger("async_collie")
LOGGING_CONFIGURED = False
HANDLER = None
LOGGING_LEVEL = None


class LoggingAlreadyConfigured(Exception):
    pass


def configure_logger(level_str: str = "info", detailed=False):
    global LOGGING_CONFIGURED
    global LOGGING_LEVEL
    global HANDLER
    HANDLER = logging.StreamHandler()

    if LOGGING_CONFIGURED:
        raise LoggingAlreadyConfigured("The logger was already configured")

    LOGGING_LEVEL = getattr(logging, level_str.upper(), logging.INFO)
    fragment_logger.setLevel(LOGGING_LEVEL)
    async_collie_logger.setLevel(LOGGING_LEVEL)

    if detailed:
        formatter = logging.Formatter("[{asctime}] {levelname}: {message}", style="{")
    else:
        formatter = logging.Formatter("{levelname}: {message}", style="{")
    HANDLER.setFormatter(formatter)

    fragment_logger.addHandler(HANDLER)
    async_collie_logger.addHandler(HANDLER)
    LOGGING_CONFIGURED = True


def teardown_logger():
    global LOGGING_CONFIGURED
    global HANDLER

    if HANDLER:
        fragment_logger.removeHandler(HANDLER)
        async_collie_logger.removeHandler(HANDLER)
        del HANDLER
        HANDLER = None
    LOGGING_CONFIGURED = False
