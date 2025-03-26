# -*- coding: utf-8 -*-
"""
Debugging functions and related stuff
"""

import os
import sys

DEBUG_ENV = os.environ.get("PYTHEIA_DEBUG")

if DEBUG_ENV and DEBUG_ENV in ("yes", "YES", "true", "TRUE", 1, "1"):
    DEBUG_ENABLED = True
    sys.stderr.write("\nDEBUG ON\n")
else:
    DEBUG_ENABLED = False


def callee():
    """
    'Black magic' to get method name. Expected to work only with CPyhton.

    """
    if not DEBUG_ENABLED:
        return True

    # noinspection PyProtectedMember
    return sys._getframe(1).f_code.co_name  # pylint: disable=W0212


def ydebug(msg=None):
    """debug in yellow"""
    if not DEBUG_ENABLED:
        return True
    if msg is None:
        msg = "\n"
    sys.stderr.write("\033[01;33m" + msg + "\033[0m" + "\n")


def pdebug(msg=None):
    """debug for plugins"""
    if not DEBUG_ENABLED:
        return True
    if msg is None:
        msg = "\n"
    sys.stderr.write("\033[01;34m" + msg + "\033[0m" + "\n")


def bdebug(msg=None):
    """debug in blue"""
    if not DEBUG_ENABLED:
        return True
    if msg is None:
        msg = "\n"
    sys.stderr.write("\033[01;36m" + msg + "\033[0m" + "\n")


def gdebug(msg=None):
    """debug in green"""
    if not DEBUG_ENABLED:
        return True
    if msg is None:
        msg = "\n"
    sys.stderr.write("\033[01;32m" + msg + "\033[0m" + "\n")


def rdebug(msg=None):
    """debug in red"""
    if not DEBUG_ENABLED:
        return True
    if msg is None:
        msg = "\n"
    sys.stderr.write("\033[01;31m" + msg + "\033[0m" + "\n")


def wdebug(msg=None):
    """debug in white"""
    if not DEBUG_ENABLED:
        return True
    if msg is None:
        msg = "\n"
    sys.stderr.write("\033[01;37m" + msg + "\033[0m" + "\n")


def debug(msg=None):
    """debug to stderr, whith no colors"""

    if not DEBUG_ENABLED:
        return True
    if msg is None:
        msg = "\n"

    sys.stderr.write(str(msg) + "\n")
    return True
