#!/usr/bin/env python

"""Logging utilities."""

import logging
import sys

from logging import Formatter

LOGGING_DEFAULT = 2


class CustomFormatter(Formatter):
    # pylint: disable=too-few-public-methods
    """Allows for ANSI coloring of logs."""
    COLORS = {
        logging.DEBUG: "[38;20m",
        logging.INFO: "[34;20m",
        logging.WARNING: "[33;20m",
        logging.ERROR: "[31;20m",
        logging.CRITICAL: "[31;1m",
    }

    def format(self, record):
        return f"\x1b{CustomFormatter.COLORS[record.levelno]}{super().format(record=record)}\x1b[0m"


def set_log_levels(verbosity: int = LOGGING_DEFAULT):
    # pylint: disable=protected-access
    """
    Assigns the logging levels in a consistent way.

    Args:
        verbosity: The logging verbosity level from  0 (least verbose) to 4 (most verbose).
    """
    levels = {
        0: logging.FATAL + 10,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
        4: logging.NOTSET,
    }

    _format = None
    # normal, quiet, silent ...
    if verbosity <= LOGGING_DEFAULT:
        _format = "%(message)s"
    # debug / verbose ...
    elif verbosity == LOGGING_DEFAULT + 1:
        _format = "%(asctime)s %(levelname)-8s %(message)s"
    # very verbose ...
    else:
        # _format = "%(asctime)s.%(msecs)d %(levelname)-8s %(name)s %(message)s"
        _format = "%(asctime)s.%(msecs)d %(levelname)-8s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"

    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        format=_format,
        level=levels[verbosity],
        stream=sys.stdout,
    )

    # No need to loop over handlers or perform None checks as we know from basicConfig() there is only one, and it has
    # a formatter assigned.
    handler = logging.getLogger().handlers[0]
    handler.formatter = CustomFormatter(fmt=handler.formatter._fmt)
