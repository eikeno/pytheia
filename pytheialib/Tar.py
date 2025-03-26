# -*- coding: utf-8 -*-
"""
Tar format support
"""

import os
import tarfile

import pytheialib


class Tar:
    """
    Tar archives manipulation
    - Extends tarfile.py and its main TarFile class
    """

    # FIXME: work on the .tar.xz and other new possible file extensions. To be seen with mime as well.

    def __init__(self):
        self.tar_file = None  # Str
        self.out_dir = None  # Str
        self.handle = None  # <tarfile.TarFile>
        self.all_files_d = None  # Dict

    def register(self, tar_file, out_dir=None):
        """
        Register tar archive for later treatment

        If equal to None, outdir will be automatically replaced by a directory
        in the current working directory, whith a name based on archive basename,
        without extension.
        """
        self.tar_file = tar_file
        self.out_dir = out_dir

        if not self.out_dir:
            self.out_dir = os.path.join(os.getcwd(), os.path.basename(os.path.splitext(self.tar_file)[0]))

        self.handle = tarfile.open(self.tar_file, "r")

    def _all_files_names(self):
        """
        Return names (keys) from 'all_files_d'.
        """
        filepath_list = []
        filepath_list.extend([n for n in self.all_files_d.keys()])

        return pytheialib.ignore_patterns_on_filepath_list(filepath_list)

    def list_all_files(self):
        """
        List files from registered archive.

        Internally maintains a members <-> TarInfo mapping for use by
        extract functions.
        """
        if not self.all_files_d:
            self.all_files_d = {}

        _members = self.handle.getmembers()

        for _member in _members:
            self.all_files_d[_member.name] = _member  # {'foo': "<TarInfo 'foo'>"}

        return self._all_files_names()

    def extract_file_tobuffer(self, member):
        """
        Extract specified 'member' from registered archive to an
        in-memory buffer that is returned.
        """
        return self.handle.extractfile(member)
