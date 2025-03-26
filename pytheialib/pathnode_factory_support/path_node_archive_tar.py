# -*- coding: utf-8 -*-
# pylint: disable=duplicate-code
"""
PathNodeArchiveTar
"""

import tempfile

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.pathnode_factory_support.path_node_mixin import PathNodeMixin
from pytheialib.Tar import Tar as TargerHandler
from pytheialib.TarItemCacheable import TarItemCacheable


class PathNodeArchiveTar(PathNodeMixin):
    """
    PathNodeArchiveTar
    """

    def __init__(self):
        PathNodeMixin.__init__(self)

        self.format_cc_name = "Tar"
        self.item_cacheable = TarItemCacheable

    def _mk_tempdirname(self):
        """
        Make a temporary, secure directory name to extract files to
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.node_temp_dir = tempfile.mkdtemp(
            suffix=".tmp", prefix="pytheia_PNATar_", dir=self.platform.pytheia_cache_dir
        )

    def _register_archive_to_backend(self):
        """
        Register the archive to the Tar backend
        """
        self.handler = TargerHandler()
        self.handler.register(self.start_uri, self.node_temp_dir)
