# -*- coding: utf-8 -*-
# pylint: disable=duplicate-code
"""
PathNodeMixin
"""

import mimetypes
import os
import shutil
import tempfile

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.Mime import Mime
from pytheialib.path_node_exceptions import PathNodeEOListError, PathNodeSOListError
from pytheialib.PathNodeAbstract import PathNodeAbstract
from pytheialib.Utils import Utils


class PathNodeMixin(PathNodeAbstract):
    """
    PathNodeMixin.

    To be inherited from and completed by overloading, depending
    on the target format.
    FIXME: use ABC here to make code inspection easier
    """

    def __init__(self):
        PathNodeAbstract.__init__(self)

        self.start_uri = None  # Str, a file or a dir
        self.supported_types = None  # List
        self._all_files = None  # List
        self.all_files = None  # List
        self.position = None  # Int

        self._current_path = None  # Str / property: current_path

        self.populated = False
        self.is_empty = None  # Bool

        # Dynamically set from factory:
        self.platform = None  # <Platform>
        self.recursive = None  # Bool
        self.cli_parse = None  # <CliParse>
        self.supporting_pool = None  # <SupportingPool>

        # to be overloaded by implementations:
        self.format_cc_name = None  # Str

        # Target specifics:
        self.handler = None  # <Rar>|<Zip>|<Tar>
        self.item_cacheable = None  # <*ItemCacheable>
        self.node_temp_dir = None  # Str (path)

    def __len__(self):
        """Handles len() calls. Returns populated files count"""
        gdebug(f"# {self.__class__}:{callee()}")

        return self.len()

    def len(self):
        """Returns populated files count for this object"""
        gdebug(f"# {self.__class__}:{callee()}")

        if not self.all_files:
            return 0
        return len(self.all_files)

    def __str__(self):
        """Text representation of this object"""

        return ("%s(current_path=%s," + " len=%s, start_uri=%s)") % (
            str(self.__class__),
            str(self._current_path),
            str(self.len()),
            str(self.start_uri),
        )

    def __repr__(self):
        """Serializable representation of this object"""
        return self.__str__()

    def _register_archive_to_backend(self):
        raise NotImplementedError("_register_archive_to_backend must be implemented by Mixin consummer")

    def _mk_tempdirname(self):
        """
        Make a temporary, secure directory name to extract files to
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.node_temp_dir = tempfile.mkdtemp(
            suffix=".tmp",
            prefix="pytheia_PNA%s_" % self.format_cc_name,
            dir=self.platform.pytheia_cache_dir,
        )

    def set_start_uri(self, uri=None):
        """
        Set or update instance 'start_uri'
        """
        gdebug("# %s:%s(uri=%s)" % (self.__class__, callee(), str(uri)))

        if not uri:
            raise TypeError("you must set uri")
        self.start_uri = uri

    def populate(self):
        """
        Perform files/resources detection and preparation for a Node.

        Calling code should do this the later possible (ie: when entering
        the node, not upon creation) to be able to manage lots of nodes, and
        be kind with slow medias (ie: network share, etc...)
        """
        bdebug("# %s:%s()" % (self.__class__, callee()))
        debug("start_uri = %s" % self.start_uri)

        self.all_files = []
        types = Mime().get_supported_mimetypes()

        # Obtain a temp dir up to unpopulate() call:
        self._mk_tempdirname()

        # Register the archive to the backend:
        self._register_archive_to_backend()

        # discover files within the archive:
        self.all_files = self.handler.list_all_files()  # should be filtered !!!

        # Remove unsupported files
        self._all_files = []

        for _file in self.all_files:
            if mimetypes.guess_type(_file)[0] in types:
                self._all_files.append(_file)

        self._all_files.sort()

        self.all_files = []
        for _file in self._all_files:
            self.all_files.append(
                self.item_cacheable(  # pylint: disable=E1102
                    self.start_uri, self.handler, self.node_temp_dir, _file
                )
            )

        if len(self.all_files) == 0:
            raise ValueError("No supported files found under: %s" % self.start_uri)

        # Point to first file of list by default:
        self.position = 0
        self.current_path = self.all_files[self.position]

        wdebug("Initial file set to: %s (at position: %s)" % (Utils.str_reduced(80, self.current_path), self.position))
        self.populated = True

    @property
    def current_path(self):
        """
        'current_path' attr. getter.
        Returns the real filepath (the one with MD5 part) for the current
        file.
        """

        # pylint: disable=E0202,E0102
        self._current_path = self.all_files[self.position].filepath_norm
        return self._current_path

    @current_path.setter
    def current_path(self, _filename):
        """
        'current_path' attr. setter.
        """

        # pylint: disable=E0202,E0102
        debug("all_files[0] = %s" % str(self.all_files[0]))
        self.all_files[self.position].filename = (
            str(_filename)
            .replace(
                # remove extraneous cache dir path:
                self.all_files[self.position].node_temp_dir,
                "",
            )
            .replace(os.path.sep, "", 1)
        )

    @current_path.deleter
    def current_path(self):
        """
        'current_path' attr. deleter.
        """

        # pylint: disable=E0202,E0102
        del self._current_path

    def unpopulate(self):
        """
        Unpopulate this PathNode from his populated files references
        """

        gdebug("# %s:%s()(start_uri=%s)" % (self.__class__, callee(), self.start_uri))
        if self.all_files:
            for _item in self.all_files:
                if _item.used:
                    _item.close()

        if self.node_temp_dir:
            rdebug(
                "Would need to delete %s, having %s entries" % (self.node_temp_dir, len(os.listdir(self.node_temp_dir)))
            )
            shutil.rmtree(self.node_temp_dir, ignore_errors=False)
        self.node_temp_dir = None

    def preaccess_current(self):
        """Make sure the cached file is available for rest of the world now.

        Intended to be called by code pieces that need early access to the
        current file in 'all_files'.
        """
        gdebug(f"# {self.__class__}:{callee()}")
        self.all_files[self.position].uncompress_file_if_needed()

    def seek(self, offset, whence):
        """
        Seek in the PathNode, given an 'offset' and 'whence' value.
        Values expected for 'whence' muse be from: 'os.SEEK_*'
        """
        gdebug("# %s:%s(%s, %s)" % (self.__class__, callee(), offset, whence))

        if not self.all_files:
            raise RuntimeError("use populate() first")

        if not self.all_files:
            self.populate()

        if len(self.all_files) <= 1:
            # Don't waste time if only one file is indexed:
            return
        _current_path_previous = self.all_files[self.position]

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
            # Relative to end
            if len(self.all_files) + offset >= len(self.all_files):
                raise PathNodeEOListError(
                    "EOL Reached",
                    (len(self.all_files) + offset) - len(self.all_files),  # extra
                )

            if len(self.all_files) + offset < 0:
                return PathNodeSOListError("SOL Reached", len(self.all_files) + offset)

            # we're inside the boundaries:
            self.position = len(self.all_files) + offset
        else:
            raise RuntimeError("Incorrect whence value: %s" % str(whence))

        try:
            _current_path_previous.__del__()
        except AttributeError:
            # only backends using *Cacheable objects are deletable
            pass

        self.current_path = self.all_files[self.position]

        debug("new position: %s" % self.position)
        return True

    def seek_first(self):
        """
        Seek to first item in 'all_files'
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.position = 0
        self.current_path = self.all_files[self.position]

    def seek_last(self):
        """
        Seek to last item in 'all_files'
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.position = len(self.all_files) - 1
        self.current_path = self.all_files[self.position]

    def __del__(self):
        debug("# %s:%s()(start_uri=%s)" % (self.__class__, callee(), self.start_uri))

        self.unpopulate()
