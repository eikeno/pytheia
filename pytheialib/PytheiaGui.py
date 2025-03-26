# -*- coding: utf-8 -*-
"""
PytheiaGui
"""

import gi # pylint: disable=import-error

from pytheialib.CreateObjects import CreateObjects
from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.Events import Events
from pytheialib.Mime import Mime

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk # pylint: disable=import-error


class PytheiaGui(Events, Mime):
    """
    Pytheia main class

    - Takes care of objects loading and setup their initial interactions / state.
    - Manage the initialization / reload sequencing.
    """

    PYTHEIA_APP_NAMES = ("Pytheia", "Image Viewer")

    def __init__(self):
        self.command_line = None  # <Str>List
        self.creator = CreateObjects(self)
        self.pytheia_exec_dir = None  # /path/to/pytheia/pytheialib/
        self.creator.create_objects()
        self.pytheia_install_context = None  # system | sources_dir
        self.plugins = None
        self.image_display_widget = None
        self.pbl = None  # ProgressivePixbufLoader

        Events.__init__(self)
        Mime.__init__(self)

    def set_pytheia_install_context(self, value):
        """
        Explicitly set value of `pytheia_install_context'

        :param value: string. One of 'system', 'sources_dir'
        """
        self.pytheia_install_context = value

    def set_pytheia_exec_dir(self, value):
        """
        Explicitly set value of `set_pytheia_exec_dir'

        :param value: string. Path to pytheialib directory.
        """
        self.pytheia_exec_dir = value

    def core(self, command_line=None):
        """
        Pytheia main loop, and Object Factory for other entities
        """
        gdebug("# %s:%s(%s)" % (self.__class__, callee(), str(command_line)))
        debug("pytheia_install_context = %s" % self.pytheia_install_context)

        if command_line is None:
            raise TypeError("a path or file path must be specified")

        if len(command_line) < 1:
            raise TypeError("a path or file path must be specified")

        self.command_line = command_line

        # True to emulate other monitors aspect ratio, to be tweaked in
        # Screen.initialize():
        # self.screen_simulation = True

        # FIXME: this would be cleaner that creator returns a special configuration object instead of
        # FIXME: adding / modifying attributes here directly
        # Create objects and setup relationships:
        self.creator.setup_objects()

        # Plugins subsystem initialization:
        self.plugins.initialize()  # attaches to <PluginsStore>, <Platform>
        self.plugins.discover_plugins()
        self.plugins.register_plugins()

        # Disable individual plugins when not explicitly enabled
        # by previously recorded state:
        self.plugins.disable_undefined_plugins()

        # Make sure the plugins manager plugin is enabled:
        self.plugins.enable_plugin("plugins_manager")
        self.plugins.register_plugin("plugins_manager")

        # show and start render:
        self.image_display_widget.main_window.show_all()
        self.pbl.pixbuf_loader_start()  # FIXME: reduce coupling here

        # Start GUI:
        Gtk.main()
