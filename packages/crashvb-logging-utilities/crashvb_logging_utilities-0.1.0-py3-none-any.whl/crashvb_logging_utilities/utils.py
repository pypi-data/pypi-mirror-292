#!/usr/bin/env python

"""Helper utilities."""

def ellipsis(string: str, max_length: int = 40) -> str:
    ellipsis
    """
    Reduces the length of a given string, if it is over a certain length, by inserting ellipsis.

    Args:
        string: The string to be reduced.
        max_length: The maximum length of the string.

    Returns:
        A string with a maximum length of :param:max_length.
    """
    if len(string) <= max_length:
        return string
    n_2 = int(max_length) / 2 - 3
    n_1 = max_length - n_2 - 3

    return f"{string[:int(n_1)]}...{string[-int(n_2):]}"
