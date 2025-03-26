# -*- coding: utf-8 -*-
"""
Platform
"""

import os
import sys
import tempfile

from pytheialib.Borg import Borg
from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.IO import IO


class Platform(Borg):
    """
    Platform portability
    """

    initialized = False
    platform_name = None  # unix | darwin | win32
    userdir = None  # home directory
    pytheia_data_dir_system = None  # /path/to/pytheia/data/
    pytheia_plugins_dir_system = None
    pytheia_data_dir_user = None  # /path/to/pytheia/data/
    pytheia_plugins_dir_user = None  # /path/to/pytheia/plugins/
    pytheia_cache_dir = None
    trashdir_fallback = None
    # these must be externally manipulated. explicit this with setters, even if not very pythonic:
    pytheia_exec_dir = None  # /path/to/pytheia/pytheialib/
    pytheia_install_context = None  # system | sources_dir

    def __init__(self):
        pass

    def set_pytheia_exec_dir(self, value):
        """
        Explicitly set value of `set_pytheia_exec_dir'

        :param value: string. Path to pytheialib directory.
        """
        self.pytheia_exec_dir = value

    def set_pytheia_install_context(self, value):
        """
        Explicitly set value of `pytheia_install_context'

        :param value: string. One of 'system', 'sources_dir'
        """
        self.pytheia_install_context = value

    def initialize(self):
        """
        Set correct values on attributes
        """
        gdebug(f"# {self.__class__}:{callee()}")

        if sys.platform == "darwin":
            self.platform_name = "darwin"

        elif sys.platform == "win32":
            self.platform_name = "win32"

        elif sys.platform == "linux2":
            self.platform_name = "unix"

        elif sys.platform.__contains__("freebsd"):
            self.platform_name = "unix"

        else:
            # Fallback to unix:
            self.platform_name = "unix"
        # FIXME: detect more platforms

        if self.platform_name in ("unix", "darwin"):
            import pwd  # pylint: disable=W0404

            self.userdir = pwd.getpwuid(os.getuid())[5]
            self.pytheia_cache_dir = os.path.join(self.userdir, ".cache", "pytheia")

        elif self.platform_name == "win32":
            self.userdir = os.environ["USERPROFILE"]  # have better ?
            self.pytheia_cache_dir = os.path.join(tempfile.gettempdir(), "pytheia")

        if not os.path.exists(self.pytheia_cache_dir):
            IO().make_folder_with_parents(self.pytheia_cache_dir)

        # Trash when GIO's approach not available:
        self.trashdir_fallback = os.path.join(self.userdir, ".config", "pytheia", "Trash")

        if self.pytheia_install_context == "system":
            self.pytheia_data_dir_system = "/usr/share/pytheia/"
            self.pytheia_plugins_dir_system = "/usr/share/pytheia/plugins/"

        elif self.pytheia_install_context == "sources_dir":
            debug("pytheia_exec_dir => %s" % self.pytheia_exec_dir)
            self.pytheia_data_dir_system = os.path.join(os.path.dirname(self.pytheia_exec_dir), "data")
            self.pytheia_plugins_dir_system = os.path.join(os.path.dirname(self.pytheia_exec_dir), "plugins")

        # independent of install context:
        self.pytheia_data_dir_user = os.path.join(self.userdir, ".local", "share", "pytheia", "data")

        self.pytheia_plugins_dir_user = os.path.join(self.userdir, ".local", "share", "pytheia", "plugins")
        self.initialized = True

        debug("userdir = %s" % self.userdir)
        debug("trashdir_fallback = %s" % self.trashdir_fallback)
        debug("pytheia_exec_dir = %s" % self.pytheia_exec_dir)
        debug("pytheia_data_dir_system = %s" % self.pytheia_data_dir_system)
        debug("pytheia_plugins_dir_system = %s" % self.pytheia_plugins_dir_system)
        debug("pytheia_data_dir_user = %s" % self.pytheia_data_dir_user)
        debug("pytheia_plugins_dir_user = %s" % self.pytheia_plugins_dir_user)

    def get_infos(self):
        """Get a dictionnary of attributes"""
        gdebug(f"# {self.__class__}:{callee()}")

        if not self.initialized:
            raise RuntimeError("initialize must be called once before !")

        return {
            "patform_name": self.platform_name,
            "userdir": self.userdir,
            "trashdir_fallback": self.trashdir_fallback,
        }
