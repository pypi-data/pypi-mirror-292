#!/usr/bin/env python

"""Logging utilities for Click."""

import click

from .logging import LOGGING_DEFAULT


def logging_options(function):
    """Common logging options."""

    function = click.option(
        "-s",
        "--silent",
        "verbosity",
        flag_value=LOGGING_DEFAULT - 2,
        help="Suppress all output.",
    )(function)
    function = click.option(
        "-q",
        "--quiet",
        "verbosity",
        flag_value=LOGGING_DEFAULT - 1,
        help="Restrict output to warnings and errors.",
    )(function)
    function = click.option(
        "-d",
        "--debug",
        "-v",
        "--verbose",
        "verbosity",
        flag_value=LOGGING_DEFAULT + 1,
        help="Show debug logging.",
    )(function)
    function = click.option(
        "-vv",
        "--very-verbose",
        "verbosity",
        flag_value=LOGGING_DEFAULT + 2,
        help="Enable all logging.",
    )(function)

    return function


@click.command()
def version():
    """Displays the version."""

    # Note: * This cannot be imported above, as it causes a circular import!
    #       * This requires '__version__' to be defined in '__init__.py'
    from . import __version__  # pylint: disable=import-outside-toplevel

    print(__version__)
