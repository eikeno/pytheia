# -*- coding: utf-8 -*-
"""RarItemCacheable"""

import os

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.Utils import Utils


class RarItemCacheable:
    """
    File Like object to point on files discovered in an archive file.

    The idea is to uncompres a file only when a read() request is made on it,
    to avoid bottleneck doing it all at once.
    """

    def __init__(self, _archive, _rar, _node_temp_dir, _file):
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), _file))

        self.archive = _archive  # Str, I.e: '/home/user/Docs/foo.cbr'
        self.rar = _rar  # <pytheialib.Rar.Rar>
        self.node_temp_dir = _node_temp_dir  # Str, I.e: '/home/foo/.cache/pytheia/pytheia_PNARar_f6e5ejd9.tmp'

        self._filepath = None  # Str
        # managed by filepath property
        # get -> /home/user/.cache/pytheia/pytheia_PNARar_f6e5ejd9.tmp/foo/img-001.jpg

        self.filepath_norm = None  # Str
        # managed by filepath property
        # get -> /home/user/.cache/pytheia/pytheia_PNARar_f6e5ejd9.tmp/[md5_data].jpg

        self._filename = None  # Str
        # managed by filename property
        # get -> 'foo/img-001.jpg'

        self.filename = _file  # Str
        # get -> 'foo/img-001.jpg'

        self.filename_norm = None  # Str
        # managed by filename property
        # get -> "b'[md5_data]'"

        self._fd = None  # <File>self.filepath

        # When no read*() where used, we can spare some closing/deleting
        # method calls. Those latest will switch to False when called, in a
        # one-way-only manner:
        self.used = False

    def __str__(self):
        """Returns string representation of 'filepath'"""
        return str(self.filepath)

    def __repr__(self):
        """Returns string representation of 'filepath'"""
        return self.__str__()

    def __len__(self):
        """Wrapper to len()"""
        return self.len()

    def rfind(self, sep):
        """Returns rfind(sep) for string representation of filepath"""
        return str(self.filepath).rfind(sep)

    def basename(self):
        """Returns basename of 'filepath'"""
        return os.path.basename(self.filepath)

    @property
    def filename(self):
        """'filename' attr. getter"""
        # pylint: disable=E0202,E0102
        return self._filename

    @filename.setter
    def filename(self, _filename):
        """
        'filename' attr. setter
        Actually sets '_filename', 'filename_norm' and 'filepath'
        """
        # pylint: disable=E0202,E0102
        self._filename = _filename
        self.filename_norm = str(Utils.md5_by_string(self._filename))
        self.filepath = _filename  # full path and md5 name

    @filename.deleter
    def filename(self):
        """'filename' attr. deleter"""
        # pylint: disable=E0202,E0102
        del self._filename
        del self.filename_norm

    @property
    def filepath(self):
        """'filepath' attr. getter"""
        # pylint: disable=E0202,E0102
        return self._filepath

    @filepath.setter
    def filepath(self, _filename):
        """
        filepath attr. setter
        Also sets filepath_norm
        """
        # pylint: disable=E0202,E0102
        self._filepath = os.path.join(self.node_temp_dir, _filename)
        _ext = os.path.splitext(self._filepath)[1]

        self.filepath_norm = os.path.join(
            self.node_temp_dir,
            str(Utils().md5_by_string(self._filename)).replace("'", "") + _ext,
        )

    @filepath.deleter
    def filepath(self):
        """'filepath' attr. deleter"""
        # pylint: disable=E0202,E0102
        del self._filepath
        del self.filepath_norm

    def _uncompress_file(self):
        """
        Uncompress 'filename' content to cache directory, using a
        an MD5 sum of the file basename + relative path inside cache, and
        appending again the clean-text extension (to avoid confusing code/tools
        possibly relying on extension rather than 'magic' mime / headers).
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.rar.extract_file_as(
            self.filename,  # member
            self.filepath_norm,  # destination file
        )

    def uncompress_file_if_needed(self):
        """
        Call _uncompress_file() unless it's already been done.
        """
        gdebug(f"# {self.__class__}:{callee()}")
        if not self.filename:
            raise RuntimeError("filename unset")

        if not self.filepath_norm:
            raise RuntimeError("filepath_norm unset")

        if not os.path.isfile(self.filepath_norm):
            self._uncompress_file()

        self._fd = open(str(self.filepath_norm), "rb")

    def len(self):
        """
        Returns size in bytes of 'self.filepath_norm'
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.uncompress_file_if_needed()
        return len(open(self.filepath_norm, "rb").read())

    def readable(self):
        """
        Returns True to indicate the readable state of the file-like object
        """
        gdebug(f"# {self.__class__}:{callee()}")
        return True

    def read(self, size=None):
        """
        Reads at most size bytes from the file.
        """
        gdebug(f"# {self.__class__}:{callee()}")
        self.used = True

        self.uncompress_file_if_needed()
        if not size:
            return self._fd.read()
        else:
            return self._fd.read(size)

    def readline(self, size):
        """
        read one entire line from the file.
        """
        gdebug(f"# {self.__class__}:{callee()}")
        self.used = True

        self.uncompress_file_if_needed()
        if not size:
            return self._fd.readline()
        else:
            return self._fd.readline(size)

    def readlines(self, size):
        """
        read one entire line from the file.
        """
        gdebug(f"# {self.__class__}:{callee()}")
        self.used = True

        self.uncompress_file_if_needed()
        if not size:
            return self._fd.readlines()
        else:
            return self._fd.readlines(size)

    # noinspection PyUnusedLocal
    def write(self, _str):
        """
        FIXME: Writes a string to the file. Not implemented
        """
        gdebug(f"# {self.__class__}:{callee()}")
        raise NotImplementedError

    def close(self):
        """
        Closes the file filedescriptor '_fd'.
        Unlink file pointed by 'filepath_norm''
        """
        wdebug("# %s(%s):%s()" % (self.__class__, self.basename(), callee()))

        if self._fd:
            self._fd.close()

        if self.filepath_norm:
            if os.path.exists(self.filepath_norm):
                try:
                    os.unlink(self.filepath_norm)
                except OSError as exc:
                    rdebug(str(exc))

    def __del__(self):
        """
        Dereference as much attributes as possible
        """
        wdebug("# %s(%s):%s()" % (self.__class__, self.basename(), callee()))

        self.close()
