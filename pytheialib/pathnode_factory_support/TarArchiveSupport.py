# -*- coding: utf-8 -*-
"""
TarArchiveSupport
"""

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.pathnode_factory_support import path_node_archive_tar


class TarArchiveSupport:
    """
    Support for TAR archive format. Based on native python support.
    """

    def __init__(self):
        self.mime_types = (
            "application/x-cbt",
            "application/x-tar",
            "application/x-gzip",
        )  # FIXME: this should be in Tar instead
        self.extensions = (
            # FIXME: find a way to handle compound extensions, I.e: tar.7z, tar.xz etc...
            ".tar",
            ".gz",
            ".tgz",
            ".bz2",
            ".xz",
            ".tbz2",
            ".cbt",
        )  # FIXME: this should be in Tar instead
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
            self.supporting_pool[_ext]["mimes"] = self.mime_types
            self.supporting_pool[_ext]["factory"] = {
                "name": "archive_tar",
                "origin": "native",
                "recursive": True,
                "uri": None,
                "provider": path_node_archive_tar.PathNodeArchiveTar,
            }
