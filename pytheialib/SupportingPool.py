# -*- coding: utf-8 -*-
"""
SupportingPool
"""

import os

from . import pathnode_factory_support
from .Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from .Mime import Mime

from .pathnode_factory_support import *
from .Utils import Utils


class SupportingPool:
    """
    Manage additional support
    """

    def __init__(self):
        self.cli_parse = None  # <CliParse>
        self.supporting_pool_d = None  # Dict
        self.path_nodes_factory = None  # <PathNodesFactory>
        self.path_index = None  # <PathIndex>

    def initialize(self):
        """
        Loads additional formats supports and make it available
        """
        gdebug(f"# {self.__class__}:{callee()}")
        _extra = None

        if not self.supporting_pool_d:
            self.supporting_pool_d = {}

        if not self.path_index:
            raise RuntimeError("path_index is not set")

        for i in pathnode_factory_support.__all__:
            exec(  # pylint: disable=W0122
                f"from .pathnode_factory_support import {i} as {i}"
            )
            # FIXME: get rid of eval()
            _extra = eval(f"{i}.{i}()")  # WhateverSupport.WhateverSupport()
            _extra.register(self.supporting_pool_d)
        del _extra
        self.path_nodes_factory.add_to_supporting_pool(self.supporting_pool_d)

    @staticmethod
    def _has_only_subdirs(_path):
        """
        Returns True if 'dir' has only directories as child, and no files
        """
        rdebug("# _has_only_subdirs(%s)" % str(_path))
        for i in os.listdir(_path):
            if not os.path.isdir(os.path.join(_path, i)):
                return False
        return True

    @staticmethod
    def lcext(ext_s):
        """
        Lowercase passed extension, but ignore special keywords such as:
        'DIRECTORY'
        """
        if ext_s in "DIRECTORY":
            return ext_s
        else:
            return ext_s.lower()

    def get_mimetypes_extended(self):
        """
        Returns a list of supported mimetypes including those from
        SupportingPool.

        """
        rdebug("# %s:%s()" % (self.__class__, callee()))

        mext = []
        for i in self.supporting_pool_d:
            if i.startswith("."):
                mext.extend(self.supporting_pool_d[i]["mimes"])

        return mext

    def evaluate(self, cli_parse_items):
        """
        Evaluate an item (file, directory, uri ...) for support and append
        it if supported.

        It can later be populated and used.
        Recursivity is enabled depending on <CliParse> values.

        """
        rdebug("# %s:%s(%s)" % (self.__class__, callee(), str(cli_parse_items)))

        _lc = self.lcext
        for _requested_path in cli_parse_items:
            _requested_path = os.path.abspath(_requested_path)
            debug("<iter> _requested_path = " + _requested_path)

            # noinspection PyUnusedLocal
            _container_dir = None

            if not os.path.isdir(_requested_path) and not os.path.isfile(_requested_path):
                # FIXME: do not always raise error here, ie: symlink case.
                # FIXME: shall we follow symlink ? How to manage broken symlinks?
                # TODO: Remove this error when protocol based res. support added
                raise ValueError("Type error, should be a file or a dir: %s" % _requested_path)

            # Match first on an additional provider based on filename extension:
            # FIXME: add some mime handling here.
            if os.path.isdir(_requested_path):
                # Directories are not extensions based, so force support here:
                _ext = "DIRECTORY"
                _container_dir = _requested_path + os.path.sep
            else:
                _ext = os.path.splitext(_requested_path)[1]
                _container_dir = os.path.dirname(_requested_path) + os.path.sep

            debug("_container_dir ===========> %s" % _container_dir)
            # Match with proper support provider, if any
            if (
                _lc(_ext) in (self.supporting_pool_d)
                and _container_dir
                not in ([i.start_uri for i in self.path_index.path_nodes_store.store if i.start_uri.endswith("/")])
                and not self._has_only_subdirs(_container_dir)
            ):
                # create a PathNode of the correct type via Factory and get
                # it stored in path_index's pathnodes_store:
                self.path_index.append_node(
                    {
                        "current": False,
                        "node_type": self.supporting_pool_d[_lc(_ext)]["factory"]["name"],
                        "node_uri": _requested_path,
                        "recursive": self.supporting_pool_d[_lc(_ext)]["factory"]["recursive"],
                    }  # Dict node_data
                )
            # Path is a file, not supported by add. support, but a native one:
            elif os.path.isfile(_requested_path) and (_lc(_ext) in Mime().get_supported_extensions()):
                # Make sure the containing directory for that file isn't
                # already registered (i.e. avoid doubloons):
                if os.path.dirname(_requested_path) + os.path.sep not in (
                    [i.start_uri for i in self.path_index.path_nodes_store.store if i.start_uri.endswith("/")]
                ):
                    self.path_index.append_node(
                        {
                            "current": False,
                            "node_type": "location_directory",
                            "node_uri": Utils.containing_directory(_requested_path),
                            "start_uri": _requested_path,
                            "recursive": self.supporting_pool_d["DIRECTORY"][("factory")]["recursive"],
                        }  # Dict node_data
                    )

            rdebug("// %s" % _requested_path)

            # Recursivity support
            if self.cli_parse.args.recursive and (os.path.isdir(_requested_path)):
                _ls = [os.path.join(_requested_path, i) for i in os.listdir(_requested_path)]

                for _item in _ls:
                    rdebug("sub eval of: %s" % _item)
                    if os.path.isdir(_item) or (_lc(_ext) in self.supporting_pool_d):
                        self.evaluate((_item,))
                    # files in this directory have already been evaluated, so
                    # we can skip them here.
