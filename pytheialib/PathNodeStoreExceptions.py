# -*- coding: utf-8 -*-
"""
PathNodeStoreError
"""


class PathNodeStoreError(Exception):
    """
    PathNodeStore Exception base class
    """

    def __init__(self, message, *errors):
        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, message)

        # Now for your custom code...
        self.errors = errors


class PathNodeStoreEOListError(PathNodeStoreError):
    """End Of List exception"""

    def __init__(self, message, *errors):
        PathNodeStoreError.__init__(self, message)
        self.errors = errors


class PathNodeStoreSOListError(PathNodeStoreError):
    """Start Of List Exception"""

    def __init__(self, message, *errors):
        PathNodeStoreError.__init__(self, message)
        self.errors = errors


class PathNodeStoreAllNodesEmpty(PathNodeStoreError):
    """All nodes are empty of files that can be displayed"""

    def __init__(self, message, *errors):
        PathNodeStoreError.__init__(self, message)
        self.errors = errors
