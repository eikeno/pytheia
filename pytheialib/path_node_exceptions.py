# -*- coding: utf-8 -*-
"""
PathNodeError
"""


class PathNodeError(Exception):
    """
    PathNode Exception base class
    """

    def __init__(self, message, *errors):
        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, message)

        # Now for your custom code...
        self.errors = errors


class PathNodeEOListError(PathNodeError):
    """End Of List exception"""

    def __init__(self, message, *errors):
        PathNodeError.__init__(self, message)
        self.errors = errors


class PathNodeSOListError(PathNodeError):
    """Start Of List Exception"""

    def __init__(self, message, *errors):
        PathNodeError.__init__(self, message)
        self.errors = errors


class PathNodeNoSupportedFiles(PathNodeError):
    """No supported files found at depth 1"""

    def __init__(self, message, *errors):
        PathNodeError.__init__(self, message)
        self.errors = errors


class PathNodeEmpty(PathNodeError):
    """No supported files found at any depth"""

    def __init__(self, message, *errors):
        PathNodeError.__init__(self, message)
        self.errors = errors
