# -*- coding: utf-8 -*-
"""
PathNodeStore
"""

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.PathNodeStoreExceptions import PathNodeStoreAllNodesEmpty


class PathNodeStore:
    """
    Holds <PathNode> objects and offer ways of manipulating them.
    - Intended to be prepared by PathIndex, instead of PytheiaGui.core
    """

    def __init__(self):
        self.store = []  # FIXME: it would be better to refactor to make this class inherit 'list' type
        self.current_pathnode_index = 0
        self.cli_parse = None  # <CliParse>
        self.callbacks = None  # <Callbacks>
        self.index = None

    def __len__(self):
        """
        Handle len() calls
        """
        gdebug(f"# {self.__class__}:{callee()}")

        return self.len()

    def len(self):
        """
        Return count of stored PathNodes in this object
        """
        gdebug(f"# {self.__class__}:{callee()}")

        if not self.store:
            raise RuntimeError("store is uninitialized")
        return len(self.store)

    def node_index(self, node):
        """
        Returns the index of a node in the store
        """

        return self.store.index(node)

    def append_node(self, node):
        """
        Append a <PathNode> object to the store
        """

        self.store.append(node)

    def current_pathnode(self):
        """
        Returns current <PathNode> object
        """

        return self.store[self.current_pathnode_index]

    def seek_first_pathnode(self, offset=0):
        """
        Seek to first (or only) PathNode in store.
        """
        wdebug("# %s:%s(offset=%s)" % (self.__class__, callee(), str(offset)))

        if len(self.store) == 0:
            raise RuntimeError("store is empty")

        if offset >= len(self.store):
            raise RuntimeError("offset too big (offset:%s, store_len:%s)" % (offset, len(self.store)))

        self.current_pathnode_index = offset

        # Recurse until we find something usable, or quit if ends
        # up on empty:
        store = self.store[self.current_pathnode_index]
        store.populate()

        wdebug(
            """
            store.is_empty = %s
            len(self.store) = %s
            store.start_uri = %s
            """
            % (store.is_empty, len(self.store), store.start_uri)
        )
        if store.is_empty == 2 and len(self.store) > 1:
            self.seek_first_pathnode(offset + 1)
        elif store.is_empty == 2 and len(self.store) < 2:
            raise PathNodeStoreAllNodesEmpty(
                "None of the scanned %s path(s) contained supported files." % len(self.store)
            )

        # If that occurs, don't go further:
        if self.current_pathnode_index >= len(self.store):
            raise RuntimeError("current_pathnode_index too big")

    def seek_last_pathnode(self):
        """
        Seek to last (or only) PathNode in store.
        """

        self.current_pathnode_index = self.store.index(self.store[-1])

    def set_current_pathnode_by_ref(self, node_ref):
        """
        Set <PathNode> referenced by its 'node_ref' (object instance)
        as the current one
        """

        self.current_pathnode_index = self.store.index(node_ref)

    def next_pathnode(self):
        """
        Returns next <PathNode> object
        """

        return self.store[self.index + 1]

    def previous_pathnode(self):
        """
        Return previous <PathNode> object
        """

        return self.store[self.index - 1]

    def seek(self, offset):
        """
        Change the current PathNode in Store
        """
        gdebug("# %s:%s(offset=%s)" % (self.__class__, callee(), str(offset)))

        if offset + self.current_pathnode_index >= len(self.store):
            if not self.cli_parse.args.loop:
                # raise PathNodeStoreEOListError('Store EOL reached')
                debug("Store EOL reached")
                self.callbacks.cb_quit("End of list reached.")
            else:
                # TODO: use offset here:
                debug("PathNodeStoreEOListError")
                if len(self.store) > 1:
                    self.seek_first_pathnode()

        elif offset + self.current_pathnode_index < 0:
            if not self.cli_parse.args.loop:
                # raise PathNodeStoreSOListError('Store SOL reached')
                debug("Store SOL reached")
                self.callbacks.cb_quit("Start of list reached.")
            else:
                # TODO: use offset here:
                debug("PathNodeStoreSOListError")
                if len(self.store) > 1:
                    self.seek_last_pathnode()
        # TODO: add code to tell a PathNode is being left (clear cache etc..)
        else:
            self.current_pathnode_index += offset
            self.store[self.current_pathnode_index].populate()

    def __del__(self):
        wdebug("# %s:%s()" % (self.__class__, callee()))

        for _pn in self.store:
            _pn.__del__()
