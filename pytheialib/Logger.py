# -*- coding: utf-8 -*-
"""
Logger
"""

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import


class Logger:
    """Logger, decorator class

    A method decorated with this decorator generate a log, if debugging
    is enable, at call-time and exit-time of the decorated method.

    Log contains class name, method name, passed arguments.
    """

    def __init__(self):
        pass

    @staticmethod
    def log(func):
        """Staticmethod to be used as decorator"""

        def ___(*args, **kwargs):
            # pylint: disable=C0111
            # FIXME: docstring missing
            try:
                gdebug(
                    "> %s.%s%s"
                    % (
                        str(args[0]).split(" ")[0].replace("<", "", 1),
                        func.__name__,
                        str(args[1:]),
                    )
                )
                try:
                    return func(*args, **kwargs)

                except Exception as exc:  # pylint: disable=W0703
                    debug("Exception in %s : %s" % (func.__name__, exc))
                    pass

            finally:
                ydebug("> %s.%s()" % (str(args[0]).split(" ")[1], func.__name__))

        return ___
