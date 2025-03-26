# -*- coding: utf-8 -*-
"""
Rar format support
"""

import os

import pytheialib
from pytheialib.CommandHelper7z import CommandHelper7z


class Rar:
    """
    Rar archives manipulation
    extends tarfile.py and its main TarFile class
    """

    def __init__(self):
        self.all_files_d = None  # Dict
        self.out_dir = None  # Str
        self.rar_file = None  # Str
        self.handle = None  # <CommandHelper7z>

    def register(self, rar_file, out_dir=None):
        """
        Register rar archive for later treatment

        If equal to None, outdir will be automatically replaced by a directory
        in the current working directory, whith a name based on archive basename,
        without extension.

        """
        self.rar_file = rar_file
        self.out_dir = out_dir
        self.handle = CommandHelper7z(rar_file)

    def _all_files_names(self):
        """
        return names (keys) from 'all_files_d'

        """
        olst = []
        for i in self.handle.listing:
            if not i.endswith(os.path.sep):
                olst.append(i)
        return pytheialib.ignore_patterns_on_filepath_list(olst)

    def list_all_files(self):
        """
        List files from registered archive.

        """
        self.handle.parse_tech_listing()
        return self._all_files_names()

    def extract_file_as(self, member, destination_file):
        """
        Extract specified 'member' from registered archive to 'destination_file'

        """
        self.handle.extract_file_as(member, destination_file)
