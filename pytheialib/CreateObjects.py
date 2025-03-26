# -*- coding: utf-8 -*-
"""
CreateObjects

This modules provides the CreateObjects class, that holds reference to a PytheiaGui object and is
in charge of setting many of its attributes, and insert required references to
other objects as well.

Attributes:
    self.pyi (obj): PytheiaGui, to be passed upon instanciation.
"""

import os
import threading

from .Callbacks import Callbacks
from .CliParse import CliParse
from .Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from .DisplayState import DisplayState
from .ImageDisplay import ImageDisplay
from .ImageDisplayWidget import ImageDisplayWidget
from .KeyBindings import KeyBindings
from .Notifications import Notifications
from .PathIndex import PathIndex
from .PathNodeFactory import PathNodeFactory
from .Persistence import Persistence
from .Platform import Platform
from .Plugins import Plugins
from .ProgressivePixbufLoader import ProgressivePixbufLoader
from .Screen import Screen
from .SourceImage import SourceImage
from .SupportingPool import SupportingPool
from .TreeStore import TreeStore


class CreateObjects:
    """
    Manage the proper creation of top-level objects and set-up
    associations, aggregations, initializations etc.
    """

    def __init__(self, pyi):
        """
        'pyi' is the parent Pytheia instance (i.e: <PytheiaGui.PytheiaGui>).
        """
        self.pyi = pyi

    def create_objects(self):
        """
        Create objects (all equals 'None')

        `config` is populated by the results of Persistence().load() and looks like:

        {
            "main_window_fallback_height":"540.0",
            "main_window_height":"None",
            "main_window_fallback_width":"2720.0",
            "fullscreen":"True",
            "zoom_step_percent":"10",
            "pytheia_valid_pickle":"True",
            "main_window_width":"None",
            "keymods":{
                "SUPER":"Gdk.ModifierType.SUPER_MASK",
                "SHIFT":"Gdk.ModifierType.SHIFT_MASK",
                "CTRL":"Gdk.ModifierType.CONTROL_MASK",
                "MOD1":"Gdk.ModifierType.MOD1_MASK"
            },
            "keybindings":[
                ("Safely quit pytheia", "0", "self.keybindings.keyvals["q"]", "self.callbacks.cb_quit"),
                ("Thumbnails navigator", "0", "self.keybindings.keyvals["t"]", "self.callbacks.cb_thumbnails_navigate"),
                [...]
                [plugins related keybindings here]
        }
        """
        gdebug(f"# {self.__class__}:{callee()}")

        self.pyi.callbacks = None  # <Callbacks>
        self.pyi.cli_parse = None  # <CliParse>
        self.pyi.config = None  # Str
        self.pyi.display_state = None  # <DisplayState>
        self.pyi.image_display = None  # <ImageDisplay>
        self.pyi.image_display_widget = None  # <ImageDisplayWidget>
        self.pyi.tree_store = None  # <TreeStore>
        self.pyi.path_index = None  # <PathIndex>
        self.pyi.path_nodes_factory = None  # <PathNodesFactory>
        self.pyi.platform = None  # <Platform>
        self.pyi.plugins = None  # <Plugins>
        self.pyi.pbl = None  # <ProgressivePixbufLoader>
        self.pyi.persistence = None  # <Persistence>
        self.pyi.keybindings = None  # <Keybindings>
        self.pyi.notifications = None  # <Notifications>
        self.pyi.screen = None  # <Screen>
        self.pyi.source_image = None  # <SourceImage>
        self.pyi.supporting_pool = None  # Dict
        self.pyi.lock = None  # <threading.Lock>

        self.pyi.pytheia_install_context = None  # Str
        self.pyi.pytheia_exec_dir = None  # Str

    def setup_objects(self):
        """
        Setup objects interactions
        """
        gdebug(f"# {self.__class__}:{callee()}")

        # lock:
        self.pyi.lock = threading.Lock()

        # Platform():
        self.pyi.platform = Platform()
        self.pyi.platform.set_pytheia_exec_dir(self.pyi.pytheia_exec_dir)
        self.pyi.platform.set_pytheia_install_context(self.pyi.pytheia_install_context)
        self.pyi.platform.initialize()

        # Persistence()
        self.pyi.config = {}
        self.pyi.persistence = Persistence()
        self.pyi.persistence.store_file = os.path.join(
            self.pyi.platform.get_infos()["userdir"],
            ".config",
            "pytheia",
            "state.pickle",
        )
        self.pyi.config = self.pyi.persistence.load()

        # CliParse():
        self.pyi.cli_parse = CliParse()
        self.pyi.cli_parse.set_config(self.pyi.config)
        self.pyi.cli_parse.initialize("Pytheia image viewer")
        self.pyi.cli_parse.parse(self.pyi.command_line)

        # PathNodesFactory():
        self.pyi.path_nodes_factory = PathNodeFactory()
        self.pyi.path_nodes_factory.platform = self.pyi.platform
        self.pyi.path_nodes_factory.cli_parse = self.pyi.cli_parse

        # SupportingPool():
        self.pyi.supporting_pool = SupportingPool()
        self.pyi.supporting_pool.cli_parse = self.pyi.cli_parse
        self.pyi.path_nodes_factory.supporting_pool = self.pyi.supporting_pool
        self.pyi.supporting_pool.path_nodes_factory = self.pyi.path_nodes_factory

        # Callbacks():
        self.pyi.callbacks = Callbacks()
        self.pyi.callbacks.platform = self.pyi.platform

        # PathIndex():
        self.pyi.path_index = PathIndex()
        self.pyi.path_index.callbacks = self.pyi.callbacks
        self.pyi.path_index.platform = self.pyi.platform
        self.pyi.path_index.cli_parse = self.pyi.cli_parse

        self.pyi.supporting_pool.path_index = self.pyi.path_index
        self.pyi.path_index.path_nodes_factory = self.pyi.path_nodes_factory
        self.pyi.path_index.initialize()  # post initialization required

        self.pyi.supporting_pool.initialize()
        self.pyi.supporting_pool.evaluate(self.pyi.cli_parse.get("remainders"))

        # Make sure the first pathnode will be used first,
        # and leave if all found nodes are empty (i.e: doesn't have files
        # that can be used for display):
        self.pyi.path_index.path_nodes_store.seek_first_pathnode()

        # TreeStore().
        # To be instantiated by caller. Allow multiple instances
        self.pyi.tree_store = TreeStore  # FIXME: provide a Factory here instead // unused in self.pyi

        # SourceImage():
        self.pyi.source_image = SourceImage()
        self.pyi.source_image.register_image(self.pyi.path_index.path_nodes_store.current_pathnode())

        # Screen()
        self.pyi.screen = Screen()

        # Screen needs a ref to the configuration store attribute:
        self.pyi.screen.set_config(self.pyi.config)
        self.pyi.screen.screen_initialize()
        debug(
            "Screen width, height, ratio: %s, %s, %s"
            % (
                self.pyi.screen.screen_width,
                self.pyi.screen.screen_height,
                self.pyi.screen.screen_ratio,
            )
        )
        self.pyi.callbacks.screen = self.pyi.screen

        # ImageDisplay():
        self.pyi.image_display = ImageDisplay()
        self.pyi.image_display.source_image = self.pyi.source_image
        self.pyi.image_display.screen = self.pyi.screen

        # DisplayState():
        self.pyi.display_state = DisplayState()
        self.pyi.display_state.set_config(self.pyi.config)
        self.pyi.display_state.lock = self.pyi.lock
        self.pyi.display_state.image_display = self.pyi.image_display
        self.pyi.display_state.source_image = self.pyi.source_image
        self.pyi.image_display.display_state = self.pyi.display_state
        self.pyi.display_state.screen = self.pyi.screen

        # change defaults values based on command line:
        if self.pyi.cli_parse.get("fullscreen"):
            self.pyi.display_state.fullscreen = True

        # Callbacks():
        self.pyi.callbacks.persistence = self.pyi.persistence
        self.pyi.callbacks.config = self.pyi.config
        self.pyi.callbacks.path_index = self.pyi.path_index
        self.pyi.callbacks.image_display = self.pyi.image_display
        self.pyi.callbacks.display_state = self.pyi.display_state
        self.pyi.callbacks.source_image = self.pyi.source_image
        self.pyi.callbacks.lock = self.pyi.lock
        self.pyi.path_index.callbacks = self.pyi.callbacks

        # Notifications()
        self.pyi.notifications = Notifications()
        self.pyi.notifications.screen = self.pyi.screen
        self.pyi.notifications.create_status_bar()
        self.pyi.callbacks.notifications = self.pyi.notifications

        # ImageDisplayWidget()
        self.pyi.image_display_widget = ImageDisplayWidget()
        self.pyi.image_display_widget.set_pytheia_install_context(self.pyi.pytheia_install_context)

        self.pyi.image_display_widget.set_app_name(self.pyi.PYTHEIA_APP_NAMES)
        self.pyi.image_display_widget.callbacks = self.pyi.callbacks
        self.pyi.image_display_widget.set_config(self.pyi.config)
        self.pyi.image_display_widget.platform = self.pyi.platform
        self.pyi.image_display_widget.display_state = self.pyi.display_state
        self.pyi.image_display_widget.create_main_window()
        self.pyi.callbacks.image_display_widget = self.pyi.image_display_widget
        self.pyi.display_state.image_display_widget = self.pyi.image_display_widget
        self.pyi.image_display_widget.image_display = self.pyi.image_display
        self.pyi.image_display_widget.source_image = self.pyi.source_image
        # Not to be confused with Gtk parenting below:
        self.pyi.notifications.main_window = self.pyi.image_display_widget.main_window
        self.pyi.image_display.image_display_widget = self.pyi.image_display_widget

        # Allow status_bar to be correctly placed in fullscreen and window mode:
        # This is pure Gtk trickery, code still need an explicit
        # main_window reference:
        self.pyi.notifications.notification_window.set_parent(self.pyi.image_display_widget.main_window)
        self.pyi.notifications.notification_window.set_transient_for(self.pyi.image_display_widget.main_window)
        # However, this could easily be pushed to Notifications()

        # Default zoom in/out by 10%:
        # FIXME: zoom_step_percent has not its place here, make it dynamic
        if "zoom_step_percent" not in self.pyi.config:
            self.pyi.config["zoom_step_percent"] = 10

        debug(
            "%s: current_path= %s"
            % (
                self,
                self.pyi.path_index.path_nodes_store.current_pathnode().current_path,
            )
        )

        # KeyBindings():
        self.pyi.keybindings = KeyBindings()
        self.pyi.keybindings.set_config(self.pyi.config)
        self.pyi.keybindings.callbacks = self.pyi.callbacks
        self.pyi.keybindings.initialize()

        # Events():
        self.pyi.image_display_widget.main_window.connect("key_press_event", self.pyi.evt_handle_key_press)
        # FIXME: check if another callback would be required to treated mouse events:
        self.pyi.image_display_widget.main_window.connect("button_press_event", self.pyi.evt_handle_key_press)

        # ProgressivePixbufLoader():
        self.pyi.pbl = ProgressivePixbufLoader()
        self.pyi.pbl.source_image = self.pyi.source_image
        self.pyi.pbl.callbacks = self.pyi.callbacks

        # ImageDisplayWidget needs a ref to ProgressivePixbufLoader:
        self.pyi.image_display_widget.pbl = self.pyi.pbl
        self.pyi.callbacks.pbl = self.pyi.pbl
        self.pyi.display_state.pbl = self.pyi.pbl
        self.pyi.image_display.pbl = self.pyi.pbl
        self.pyi.pbl.image_display = self.pyi.image_display
        self.pyi.pbl.image_display_widget = self.pyi.image_display_widget
        self.pyi.pbl.platform = self.pyi.platform

        # Plugins():
        # Add this shortcut to the methods exposed to plug-ins:
        # Note: <PytheiaPlugins>pytheia_plugins is dynamically added by __main__:

        # noinspection PyPep8
        plug = lambda *args: pdebug(str(args[0]))
        self.pyi.pytheia_plugins.plugin_console_out = plug
        # FIXME: plugin_console_out feature is to be re-implemented completely. Not enough isolation

        self.pyi.plugins = Plugins()
        self.pyi.pbl.plugins = self.pyi.plugins
        self.pyi.display_state.plugins = self.pyi.plugins

        if self.pyi.pytheia_install_context == "system":
            self.pyi.plugins.set_plugins_search_path(
                (
                    self.pyi.platform.pytheia_plugins_dir_system,
                    self.pyi.platform.pytheia_plugins_dir_user,
                )  # paths_t
            )
        elif self.pyi.pytheia_install_context == "sources_dir":
            # FIXME: define ONLY an in-source location for plugins when ran from sources dir
            self.pyi.plugins.set_plugins_search_path(
                (self.pyi.platform.pytheia_plugins_dir_system,)  # paths_t
            )
        else:
            raise ValueError("Wrong pytheia_install_context value")

        # FIXME: avoid duplication / overlapping of self.plugins.pytheia_plugins:
        self.pyi.plugins.pytheia_plugins = self.pyi.pytheia_plugins  # pylint: disable=W0201
        self.pyi.plugins.keybindings = self.pyi.keybindings  # <KeyBindings>
        self.pyi.plugins.notifications = self.pyi.notifications  # <Notifications>
        self.pyi.plugins.main_window = self.pyi.image_display_widget.main_window  # <ImageDisplayWidget>
        self.pyi.plugins.tree_store = self.pyi.tree_store  # <TreeStore> // unused
        self.pyi.plugins.screen = self.pyi.screen  # <Screen>
        self.pyi.plugins.path_index = self.pyi.path_index  # <PathIndex>
        self.pyi.callbacks.plugins = self.pyi.plugins
