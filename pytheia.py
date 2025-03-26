#!/usr/bin/env python3
# *-* coding: utf-8 *-*
"""
In-place startup script for the application.
Calls a different entry point to the code compared to the launcher script
installed by setuptools, allowing to isolate execution to this source tree
even if already deployed system wide.
"""
# FIXME: explanation are to be given regarding plugins. Solution might be using symlinks in a pre-determined place

import sys

if __name__ == "__main__":
    import pytheialib
    from pytheialib.Debug import debug

    debug("__main__:argv=%s" % sys.argv)
    pytheialib.main_from_srcdir()  # defined in pytheialib.__init__
