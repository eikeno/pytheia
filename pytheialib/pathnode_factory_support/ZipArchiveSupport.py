# -*- coding: utf-8 -*-
"""
ZipArchiveSupport
"""

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.pathnode_factory_support import path_node_archive_zip


class ZipArchiveSupport:
    """
    Support for ZIP archive format
    Based on native python support.
    """

    def __init__(self):
        self.mime_types = ("application/x-cbz", "application/x-zip")
        self.extensions = (".zip", ".cbz")
        self.supporting_pool = None  # Dict

    def register(self, supporting_pool):
        """
        Register support for this kind or archives to the global
        'supporting_pool'
        """
        gdebug(f"# {self.__class__}:{callee()}")
        self.supporting_pool = supporting_pool

        for _ext in self.extensions:
            self.supporting_pool[_ext] = {}
            supporting_pool[_ext]["mimes"] = self.mime_types
            supporting_pool[_ext]["factory"] = {
                "name": "archive_zip",
                "origin": "native",
                "recursive": True,
                "uri": None,
                "provider": path_node_archive_zip.PathNodeArchiveZip,
            }
