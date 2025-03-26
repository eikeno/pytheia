# -*- coding: utf-8 -*-
"""
Persistence
"""

import os
import pickle

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.IO import IO
from pytheialib.Utils import Utils


class Persistence:
    """
    Data persistence using serialization
    """

    def __init__(self):
        self.__store_file = None  # str

    # noinspection PyMethodParameters
    @property
    def store_file(self):
        """`store_file` property attribute."""
        return self.__store_file

    @store_file.setter
    def store_file(self, store_file):
        self.__store_file = store_file

    @store_file.deleter
    def store_file(self):
        del self.__store_file

    def load(self):
        """
        Load pickle
        """
        gdebug(f"# {self.__class__}:{callee()}")

        if not os.path.exists(self.store_file):
            self.create_store()
            debug("Created new store_file : %s " % self.store_file)

        pickle_data = pickle.load(open(self.store_file, "rb"))

        if isinstance(pickle_data, type(None)):
            pickle_data = {}

        # Use 'pytheia_valid_pickle' sanity check field:
        try:
            if pickle_data["pytheia_valid_pickle"]:
                pass
        except KeyError:
            pickle_data["pytheia_valid_pickle"] = True

        # Make sure it's sync'd to disk before dump() is called:
        self.dump(source_object=pickle_data)

        return pickle_data

    def dump(self, source_object):
        """
        Dumps pickle.
        """
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), Utils.str_reduced(500, source_object)))

        if not os.path.isdir(os.path.dirname(self.store_file)):
            os.makedirs(os.path.dirname(self.store_file))

        # Don't catch exceptions here, and let them be propagated:
        outfile = open(self.store_file, "wb")
        pickle.dump(source_object, outfile)
        outfile.close()

        return True

    def create_store(self):
        """
        Creates pickle store_file.
        """
        gdebug(f"# {self.__class__}:{callee()}")

        if not self.store_file:
            raise TypeError("store_file cannot be None")

        if os.path.isdir(self.store_file):
            raise RuntimeError("store_file cannot be a directory")

        if os.path.exists(self.store_file):
            raise RuntimeError("store_file must not exist yet")

        # Create directory path as needed:
        if not os.path.isdir(os.path.dirname(self.store_file)):
            IO().make_folder_with_parents(os.path.dirname(self.store_file))

        with open(self.store_file, "wb") as store_file_fd:
            pickle.dump({}, store_file_fd)

        return True
