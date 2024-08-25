
import sys


def caller_name():
    """
    Returns a string with the name of the function it's called from.
    From:
    https://stackoverflow.com/questions/5067604/determine-function-name-from-within-that-function-without-using-traceback
    comment by nerdfever.com at Apr 14 at 23:09.
    Consulted: 2021-11-28 11:47.
    """

    return sys._getframe(1).f_code.co_name


