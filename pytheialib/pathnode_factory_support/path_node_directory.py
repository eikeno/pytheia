# -*- coding: utf-8 -*-
# pylint: disable=duplicate-code
"""
PathNodeDirectory
"""

import mimetypes
import os

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.Mime import Mime
from pytheialib.path_node_exceptions import PathNodeEOListError, PathNodeSOListError
from pytheialib.pathnode_factory_support.path_node_mixin import PathNodeMixin
from pytheialib.Utils import Utils


class PathNodeDirectory(PathNodeMixin):
    """
    Support of local filesystem directories and files as PathNode
    """

    def __init__(self):
        PathNodeMixin.__init__(self)

        self.populated = None  # Bool
        self.is_empty = None  # Int

        # dynamically set from factory:
        self.platform = None  # <Platform>
        self.recursive = None  # Bool
        self.cli_parse = None  # <CliParse>
        self.supporting_pool = None  # <SupportingPool>

        self.format_cc_name = "Dir"

    def populate(self):
        """
        Populate: perform files/resources detection and preparation for a Node

        Calling code should do this the later possible (ie: when entering
        the node, not upon creation) to be able to manage lots of nodes, and
        be kind with slow medias (ie: network share, etc...)
        """
        bdebug("# %s:%s()" % (self.__class__, callee()))
        debug("start_uri = %s" % self.start_uri)

        self.all_files = []
        _requested_path_isfile = None
        types = Mime().get_supported_mimetypes()
        # Support starting from a filename instead of a directory.
        # the containing directory will be scanned anyway:
        if os.path.isfile(self.start_uri):  # FILE
            # Remember the filename to position index on it after sorting:
            _requested_path_isfile = self.start_uri

            # substitute containing directory name to fall back a 'normal'
            # call by directory situation:
            self.start_uri = Utils.containing_directory(self.start_uri)

        # if dir -> nothing to do
        if not os.path.isdir(self.start_uri):  # not FILE nor DIR
            raise TypeError("%s cannot be identified correctly" % self.start_uri)

        self.all_files = [os.path.join(self.start_uri, x) for x in os.listdir(self.start_uri)]

        # Remove unsupported files
        self.all_files = [_f for _f in (self.all_files) if mimetypes.guess_type(_f)[0] in types]

        self.all_files.sort()
        self.populated = True

        debug("type of self.all_files: %s" % str(self.all_files))

        if len(self.all_files) == 0:
            self.is_empty = 2
            return

        # Point to specified file, if relevant:
        if _requested_path_isfile and _requested_path_isfile in self.all_files:
            self.position = self.all_files.index(_requested_path_isfile)
            self.current_path = self.all_files[self.position]
        else:
            self.position = 0
            self.current_path = self.all_files[self.position]

    def unpopulate(self):
        """
        Unpopulate thos PathNode from his populated files references
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.supported_types = None  # List
        self.all_files = None  # List
        self.position = None  # Int
        self.populated = None  # Bool
        self.is_empty = None  # Int

    def preaccess_current(self):
        pass

    def seek(self, offset, whence):
        """
        Seek in the PathNode, given an 'offset' and 'whence' value.
        Values expected for 'whence' muse be from: 'os.SEEK_*'
        """
        gdebug("# %s:%s(%s, %s)" % (self.__class__, callee(), offset, whence))

        if not self.all_files:
            self.populate()

        if len(self.all_files) <= 1:
            # Don't waste time if only one file is indexed:
            return

        if whence == os.SEEK_SET:
            # Absolute:
            if offset >= len(self.all_files):
                raise PathNodeEOListError(
                    "EOL Reached",
                    (offset - len(self.all_files)),  # extra
                )
            if offset < 0:
                raise PathNodeSOListError(
                    "SOL Reached",
                    offset,  # extra
                )
            # we're inside the boundaries:
            self.position = offset

        elif whence == os.SEEK_CUR:
            # Relative to current position:
            if self.position + offset >= len(self.all_files):
                raise PathNodeEOListError(
                    "EOL Reached",
                    (self.position + offset) - len(self.all_files),  # extra
                )
            if self.position + offset < 0:
                raise PathNodeSOListError(
                    "SOL Reached",
                    self.position + offset,  # extra
                )
            # we're inside the boundaries:
            self.position = self.position + offset

        elif whence == os.SEEK_END:
            if len(self.all_files) + offset >= len(self.all_files):
                raise PathNodeEOListError(
                    "EOL Reached",
                    (len(self.all_files) + offset) - len(self.all_files),  # extra
                )
            if len(self.all_files) + offset < 0:
                return PathNodeSOListError("SOL Reached", len(self.all_files) + offset)

            # We're inside the boundaries:
            self.position = len(self.all_files) + offset
        else:
            raise RuntimeError("Incorrect whence value: %s" % str(whence))

        self.current_path = self.all_files[self.position]
        debug("new position: %s" % self.position)
        return True

    def seek_first(self):
        # FIXME: comment needed
        gdebug(f"# {self.__class__}:{callee()}")

        if not self.populated:
            self.populate()

        self.position = 0
        self.current_path = self.all_files[self.position]

    def seek_last(self):
        # FIXME: comment needed
        gdebug(f"# {self.__class__}:{callee()}")

        if not self.populated:
            self.populate()
        self.position = len(self.all_files) - 1
        self.current_path = self.all_files[self.position]

    @property
    def current_path(self):
        """
        'current_path' attr. getter.
        Returns the real filepath for the current file.
        """
        # pylint: disable=E0202,E0102
        return self._current_path

    @current_path.setter
    def current_path(self, _filename):
        """
        'current_path' attr. setter.
        """
        # pylint: disable=E0202,E0102,W0221
        self._current_path = str(_filename)

    @current_path.deleter
    def current_path(self):
        """
        'current_path' attr. deleter.
        """
        # pylint: disable=E0202,E0102
        del self._current_path
