# -*- coding: utf-8 -*-
"""
DirectoryLocationSupport
"""

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.pathnode_factory_support import path_node_directory


class DirectoryLocationSupport:
    """
    Support for Directory locations. Based on native python support.
    """

    def __init__(self):
        self.mime_types = ()
        self.extensions = ("DIRECTORY",)  # Tuple. Don't remove the comma
        self.supporting_pool = None  # Dict

    def register(self, supporting_pool):
        """
        Register support for this kind or archives to the global 'supporting_pool'
        """
        gdebug("# %s:%s(supporting_pool=%s)" % (self.__class__, callee(), str(supporting_pool)))
        self.supporting_pool = supporting_pool

        for _ext in self.extensions:
            self.supporting_pool[_ext] = {}
            supporting_pool[_ext]["mimes"] = self.mime_types
            supporting_pool[_ext]["factory"] = {
                "name": "location_directory",
                "origin": "native",
                "recursive": True,
                "uri": None,
                "provider": path_node_directory.PathNodeDirectory,
            }
