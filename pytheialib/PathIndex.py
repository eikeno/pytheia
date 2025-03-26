# -*- coding: utf-8 -*-
"""
PathIndex
"""

import os

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.path_node_exceptions import PathNodeEOListError, PathNodeSOListError
from pytheialib.PathNodeStore import PathNodeStore
from pytheialib.PathNodeStoreExceptions import (
    PathNodeStoreEOListError,
    PathNodeStoreSOListError,
)


class PathIndex:
    """
    Represents the discovered paths (files) and gives ways to interact with
    these.
    """

    def __init__(self):
        self.platform = None  # <Platform>
        self.callbacks = None  # <Callbacks>
        self.cli_parse = None  # <CliParse>

        self.path_nodes_factory = None  # <PathNodesFactory>
        self.path_nodes_store = None  # <PathNodesStore>

    def initialize(self):
        """
        Append a <PathNodeStore> and a <PathNodeFactory> to the object as
        required.
        """
        if not hasattr(self, "path_nodes_store"):
            self.path_nodes_store = PathNodeStore()

        if not self.path_nodes_store:
            self.path_nodes_store = PathNodeStore()
            self.path_nodes_store.cli_parse = self.cli_parse
            if self.callbacks:
                self.path_nodes_store.callbacks = self.callbacks
            else:
                raise RuntimeError("callbacks is not set")

        if not self.path_nodes_factory:
            raise RuntimeError("path_nodes_factory is not set")

    def append_node(self, node_data=None):
        """
        Append a <PathNode> to the <PathNodesStore>, creating it based on
        provided 'node_data' indications, using <PathNodesFactory>
        """
        gdebug("# %s:%s(node_data=%s)" % (self.__class__, callee(), str(node_data)))

        _start_uri = None
        _recursive = None

        if node_data:
            if "start_uri" in node_data:
                _start_uri = node_data["start_uri"]

            _recursive = bool("recursive" in node_data)

            if (
                "node_uri" in node_data
                and (node_data["node_type"] == "location_directory")
                and not (node_data["node_uri"].endswith(os.path.sep))
            ):
                node_data["node_uri"] += os.path.sep

        new_node = self.path_nodes_factory.create_node(
            node_data["node_type"],
            node_data["node_uri"],
            recursive=_recursive,
            start_uri=_start_uri,
        )  # PathNode

        self.path_nodes_store.append_node(new_node)

    @staticmethod
    def _repr_seektype(seekval):
        """
        Display literal name of one of os.SEEK_* values, passed by
        integer value
        """
        sdict = {}
        for i in dir(os):
            if i.startswith("SEEK_"):
                # FIXME: get rid of the eval()
                sdict[eval("os.%s" % i)] = i

        return sdict[seekval]

    def seek(self, offset, whence):
        """
        Proxy to the different PathNode types seek() method, providing
        abstraction over their specific nature.
        """
        wdebug("# %s:%s(%s, %s)" % (self.__class__, callee(), offset, self._repr_seektype(whence)))
        _prev = self.path_nodes_store.current_pathnode()
        _prev_id = id(_prev)

        # skip empty nodes:
        if self.path_nodes_store.current_pathnode().is_empty == 2:
            self.path_nodes_store.seek(1)
            self.seek(offset, whence)
            return

        try:
            self.path_nodes_store.current_pathnode().seek(offset, whence)

        # End of list reached
        except PathNodeEOListError as exc:
            ydebug("<exc> PathNodeEOListError : %s" % str(exc))
            wdebug("Moving Forward")
            try:
                self.path_nodes_store.seek(1)
            except PathNodeStoreEOListError as exc:
                ydebug("<exc> PathNodeStoreEOListError : %s" % str(exc))
                self._seek_eol_reached(_prev, _prev_id)

            self.path_nodes_store.current_pathnode().populate()
            if self.path_nodes_store.current_pathnode().is_empty == 2:
                self.path_nodes_store.current_pathnode().unpopulate()
                self.path_nodes_store.seek(1)
                self.seek(offset, whence)
                return

            self.path_nodes_store.current_pathnode().seek_first()
            if _prev_id != id(self.path_nodes_store.current_pathnode()):
                _prev.unpopulate()

        # Start of list reached
        except PathNodeSOListError as exc:
            ydebug("<exc> PathNodeSOListError: %s " % str(exc))
            wdebug("Moving backward")

            try:
                self.path_nodes_store.seek(-1)
            except PathNodeStoreSOListError as exc:
                ydebug("<exc> PathNodeStoreSOListError: %s" % str(exc))
                self._seek_sol_reached(_prev, _prev_id)

            self.path_nodes_store.current_pathnode().populate()

            if self.path_nodes_store.current_pathnode().is_empty == 2:
                self.path_nodes_store.current_pathnode().unpopulate()
                self.path_nodes_store.seek(-1)
                return

            self.path_nodes_store.current_pathnode().seek_last()
            if _prev_id != id(self.path_nodes_store.current_pathnode()):
                _prev.unpopulate()

    def _seek_sol_reached(self, _prev, _prev_id):
        if self.cli_parse.args.loop:
            # loop to last node in store:
            # Reset current PathNode position before switching:
            self.path_nodes_store.seek_last_pathnode()
            _cur = self.path_nodes_store.current_pathnode()
            _cur_id = id(_cur)

            if _cur_id != _prev_id:
                self.path_nodes_store.current_pathnode().populate()
                _prev.unpopulate()
            self.path_nodes_store.current_pathnode().seek_last()
        else:
            self.callbacks.cb_quit()

    def _seek_eol_reached(self, _prev, _prev_id):
        if self.cli_parse.args.loop:
            # loop to first node in store:
            # Reset current PathNode position before switching:
            self.path_nodes_store.seek_first_pathnode()
            _cur = self.path_nodes_store.current_pathnode()
            _cur_id = id(_cur)

            if _cur_id != _prev_id:
                self.path_nodes_store.current_pathnode().populate()
                _prev.unpopulate()

            self.path_nodes_store.current_pathnode().seek_first()

        else:
            # if 'loop' option is not active, just quit:
            self.callbacks.cb_quit()

    def pathnode_seek_next(self):
        """
        Seek to next registered PathNode. triggers node population
        """
        wdebug("# %s:%s()" % (self.__class__, callee()))
        _prev = self.path_nodes_store.current_pathnode()
        _prev_id = id(_prev)

        debug("<<<<<<< %s" % self.path_nodes_store.current_pathnode_index)
        self.path_nodes_store.seek(+1)
        debug("<<<<<<< %s" % self.path_nodes_store.current_pathnode_index)
        _cur = self.path_nodes_store.current_pathnode()
        _cur_id = id(_cur)

        if _cur_id != _prev_id:
            _cur.populate()
            _prev.unpopulate()

    def pathnode_seek_previous(self):
        """
        Seek to previous registered PathNode. triggers node population
        """
        wdebug("# %s:%s()" % (self.__class__, callee()))
        _prev = self.path_nodes_store.current_pathnode()
        _prev_id = id(_prev)

        self.path_nodes_store.seek(-1)
        _cur = self.path_nodes_store.current_pathnode()
        _cur_id = id(_cur)

        if _cur_id != _prev_id:
            _cur.populate()
            _prev.unpopulate()

    def __del__(self):
        wdebug("# %s:%s()" % (self.__class__, callee()))
        self.path_nodes_store.__del__()
