# -*- coding: utf-8 -*-
"""
Defines some global values and functions
"""

import os
import re
import sys

from .Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from .PytheiaGui import PytheiaGui

# Define, globally,  patterns to be found in filepath to be totally ignored:
IGNORE_PATTERNS = {"match": (r"(.+|\A|/)__MACOSX/(.+|\Z)",)}


def ignore_patterns_on_filepath_list(filepaths_list):
    """
    Use 'IGNORE_PATTERNS' as defined in this module global section to filter out
    filepaths matching the ignore list. This gives a way to ignore unwanted files
    like '__MACOSX' dirs and such.
    """
    # FIXME: filtering as this will work with only one pattern : revamp this
    out_l = []
    for ignore_type in IGNORE_PATTERNS:
        if ignore_type == "match":
            for ignore_statement in IGNORE_PATTERNS["match"]:
                for filepath in filepaths_list:
                    if not re.match(ignore_statement, filepath):
                        out_l.append(filepath)

    return out_l


def n_percent_of(npercent, value):
    """
    Return 'npercent' percents of 'value'
    """
    return (float(value) / 100) * float(npercent)


def main_from_srcdir():
    """
    Entry point for the sources local launcher
    """
    debug("main_from_srcdir(%s)" % sys.argv)
    main(context="sources_dir")


def main(context="system"):
    """
    Entry point for the system-wide launcher script
    """
    debug("main(%s)" % sys.argv)

    # resolve locations:
    try:
        # imported ?
        _file = __file__

    except NameError:
        # run as a script ?
        _file = sys.argv[0]

    # Composed PytheiaPlugins class can be used from plugins, and act as a
    # 'gateway' to all internal Pytheia attributes/methods:
    # FIXME: needs heavy refactoring, replacing injected  pytheia_plugins object by proper pattern
    PytheiaGui.pytheia_plugins = type("PytheiaPlugins", (object,), {"it_worked": True, "yes_really": True})

    gui = PytheiaGui()
    gui.set_pytheia_exec_dir(os.path.abspath(os.path.dirname(_file)))
    gui.set_pytheia_install_context(context)

    # For now, there's nothing to be done if no file / path is specified,
    # might change in the future:
    if len(sys.argv) == 1:
        print("Nothing to do - leaving")
        sys.exit(0)

    # Catch special CLI options to help debugging, simulating devices
    # with various aspect ratio. Forced size windowed mode simulation
    # results on fullscreen / best_fit mode on the simulated device:
    #
    # Note: this is applied to the main window only, no other widgets.
    if sys.argv[1] in (
        "sim_square_screen",
        "sim_landscape_screen",
        "sim_vertical_screen",
    ):
        gui.screen_simulation = sys.argv[1]
        _args = sys.argv[2:]  # raise except if no more args passed, as intended
    else:
        _args = sys.argv[1:]

    gui.core(_args)
