# crashvb-logging-utilities

[![pypi version](https://img.shields.io/pypi/v/crashvb-logging-utilities.svg)](https://pypi.org/project/crashvb-logging-utilities)
[![build status](https://github.com/server27nw/crashvb-logging-utilities/actions/workflows/main.yml/badge.svg)](https://github.com/server27nw/crashvb-logging-utilities/actions)
[![coverage status](https://coveralls.io/repos/github/server27nw/crashvb-logging-utilities/badge.svg)](https://coveralls.io/github/server27nw/crashvb-logging-utilities)
[![python versions](https://img.shields.io/pypi/pyversions/crashvb-logging-utilities.svg?logo=python&logoColor=FBE072)](https://pypi.org/project/crashvb-logging-utilities)
[![linting](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![license](https://img.shields.io/github/license/server27nw/crashvb-logging-utilities.svg)](https://github.com/server27nw/crashvb-logging-utilities/blob/master/LICENSE.md)

## Overview

Consolidation of logging utilities.

## Installation
### From [pypi.org](https://pypi.org/project/crashvb-logging-utilities/)

```
$ pip install crashvb-logging-utilities
```

### From source code

```bash
$ git clone https://github.com/server27nw/crashvb-logging-utilities
$ cd crashvb-logging-utilities
$ virtualenv env
$ source env/bin/activate
$ python -m pip install --editable .[dev]
```

## Usage

```python
import click
import logging
import sys
from traceback import print_exception
from typing import NamedTuple

from click.core import Context
from crashvb_logging_utilities import LOGGING_DEFAULT, logging_options, set_log_levels

LOGGER = logging.getLogger(__name__)

class TypingContextObject(NamedTuple):
    # pylint: disable=missing-class-docstring
    ...
    verbosity: int

@click.group()
@logging_options
@click.pass_context
def cli(
    context: Context,
    verbosity: int = LOGGING_DEFAULT,
):
    """Main group."""

    if verbosity is None:
        verbosity = LOGGING_DEFAULT

    set_log_levels(verbosity)

    context.obj = TypingContextObject(
        # ...
        verbosity=verbosity,
    )

@cli.command(name="command1", ...)
@click.option( ... )
@click.pass_context
def command1(context: Context, ...):
    """Command #1"""
    ctx = context.obj
    try:
	    ...
    except Exception as exception:  # pylint: disable=broad-except
        if ctx.verbosity > 0:
            logging.fatal(exception)
        if ctx.verbosity > LOGGING_DEFAULT:
            exc_info = sys.exc_info()
            print_exception(*exc_info)
        sys.exit(1)
    
```

### Environment Variables

| Variable | Default Value | Description |
| ---------| ------------- | ----------- |

## Development

[Source Control](https://github.com/server27nw/crashvb-logging-utilities)
