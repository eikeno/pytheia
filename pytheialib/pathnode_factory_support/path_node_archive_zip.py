# -*- coding: utf-8 -*-
# pylint: disable=duplicate-code
"""
PathNodeArchiveZip
"""

import tempfile

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.pathnode_factory_support.path_node_mixin import PathNodeMixin
from pytheialib.Zip import Zip as TargerHandler
from pytheialib.ZipItemCacheable import ZipItemCacheable


class PathNodeArchiveZip(PathNodeMixin):
    """
    PathNodeArchiveZip
    """

    def __init__(self):
        PathNodeMixin.__init__(self)

        self.format_cc_name = "Zip"
        self.item_cacheable = ZipItemCacheable

    def _mk_tempdirname(self):
        """
        Make a temporary, secure directory name to extract files to
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.node_temp_dir = tempfile.mkdtemp(
            suffix=".tmp", prefix="pytheia_PNAZip_", dir=self.platform.pytheia_cache_dir
        )

    def _register_archive_to_backend(self):
        """
        Register the archive to the Zip backend
        """
        _zip_dict = {self.start_uri: self.node_temp_dir}
        self.handler = TargerHandler()
        self.handler.register(_zip_dict)
