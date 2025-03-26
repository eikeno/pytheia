# -*- coding: utf-8 -*-
"""
RarArchiveSupport
"""

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.pathnode_factory_support import path_node_archive_rar


class RarArchiveSupport:
    """
    Support for RAR archive format. Based on native python support.
    """

    def __init__(self):
        # Take advantage to the use of external P7zip binary to take in charge
        # other format here (like .7z archives):
        self.mime_types = (
            "application/x-rar",
            "application/x-cbr",
            "application/x-7z-compressed",
        )
        self.extensions = (".rar", ".cbr", ".7z")
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
                "name": "archive_rar",
                "origin": "optional",
                "recursive": True,
                "uri": None,
                "provider": path_node_archive_rar.PathNodeArchiveRar,
            }
