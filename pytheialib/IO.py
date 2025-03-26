# -*- coding: utf-8 -*-
"""
IO
"""

import errno
import os
import shutil
import stat

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import


class IO:
    """
    I/O helper methods
    """

    def __init__(self):
        debug("# %s:%s()" % (self.__class__, callee()))
        self.listdir_recur_onlyfiles_l = None

    def _handle_folder_ro(self, func, path, exc):
        """
        Exception handler for remove_folder_recur.
        Handles read-only files/dirs trying to change perms in a portable way.
        FIXME: not sure if what's done here work in Python3.
        """
        debug("# %s:%s()" % (self.__class__, callee()))
        excvalue = exc[1]  # this probably doesn't work

        if func in (os.rmdir, os.remove, os.makedirs) and (excvalue.errno == errno.EACCES):
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # eq. 0777
            func(path)

        else:
            raise exc

    def remove_folder_recur(self, folder):
        """
        Recursively delete folder, its sub-folders, and any others files.
        FIXME: unused, should be fixed/tested beforehand
        """
        debug("# %s:%s(%s)" % (self.__class__, callee(), str(folder)))

        shutil.rmtree(folder, ignore_errors=False, onerror=self._handle_folder_ro)
        return True

    def make_folder_with_parents(self, folder):
        """
        Create folder with its parent parts if not existing
        """
        debug("# %s:%s()" % (self.__class__, callee()))

        try:
            os.makedirs(folder)

        except OSError as exc:  # FIXME: probably buggy as hell, check this in depth
            self._handle_folder_ro(
                self.make_folder_with_parents,  # func
                folder,
                exc,
            )

    def listdir_recur_onlyfiles(self, start_dir):
        """
        recursively list files, with their full path under 'start_dir'
        """

        if not self.listdir_recur_onlyfiles_l:
            self.listdir_recur_onlyfiles_l = []

        for i in os.listdir(start_dir):
            item = os.path.join(start_dir, i)

            if os.path.isdir(item):
                self.listdir_recur_onlyfiles(item)
            elif os.path.isfile(item):
                self.listdir_recur_onlyfiles_l.append(item)

        return self.listdir_recur_onlyfiles_l
