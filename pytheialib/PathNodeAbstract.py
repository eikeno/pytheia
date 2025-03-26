# -*- coding: utf-8 -*-
"""
PathNodeAbstract
"""


class PathNodeAbstract:
    """
    Abstract class for implementing PathNode types.
    FIXME: use ABC here
    """

    def __init__(self):
        pass

    def __len__(self):
        """pseudo-interface placeholder"""
        raise NotImplementedError()

    def len(self):
        """pseudo-interface placeholder"""
        raise NotImplementedError()

    def __str__(self):
        """pseudo-interface placeholder"""
        raise NotImplementedError()

    def __repr__(self):
        """pseudo-interface placeholder"""
        raise NotImplementedError()

    def set_start_uri(self, uri=None):
        """pseudo-interface placeholder"""
        raise NotImplementedError()

    def populate(self):
        """pseudo-interface placeholder"""
        raise NotImplementedError()

    def preaccess_current(self):
        """pseudo-interface placeholder"""
        raise NotImplementedError()

    def unpopulate(self):
        """pseudo-interface placeholder"""
        raise NotImplementedError()

    def seek(self, offset, whence):
        """pseudo-interface placeholder"""
        raise NotImplementedError()

    def seek_first(self):
        """pseudo-interface placeholder"""
        raise NotImplementedError()

    def seek_last(self):
        """pseudo-interface placeholder"""
        raise NotImplementedError()

    def __del__(self):
        """pseudo-interface placeholder"""
        raise NotImplementedError()
