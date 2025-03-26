# -*- coding: utf-8 -*-
"""
PluginsStore
"""

import os

from pytheialib.Debug import *  # pylint: disable=wildcard-import,unused-wildcard-import
from pytheialib.Persistence import Persistence
from pytheialib.Platform import Platform


class PluginsStore:
    """
    Hold Plugins meta-data and objects

    The most import attribute is 'plugins', with the following structure:

    plugins:  {
        plugin_name: {
            'path:' str,
            'enabled': bool,
            'registered': bool
        }
    }
    """

    def __init__(self):
        self.platform = None  # <Platform>
        self.persistence = None  # <Persistence>

        self.plugins = None  # Dict
        self.config = None  # Dict
        self.default_state = False  # Bool

        if self.plugins:
            raise RuntimeError("plugins should be None")

        self.platform = Platform()
        # self.platform.initialize()
        self.persistence = Persistence()

        self.persistence.store_file = os.path.join(
            Platform().get_infos()["userdir"],
            ".config",
            "pytheia",
            "plugins_store.pickle",
        )

        self.config = self.persistence.load()

        if "plugins" not in self.config:
            wdebug("self.config['plugins'] = {}")
            self.config["plugins"] = {}
        self.plugins = self.config["plugins"]

    def add(self, plugin, path, state, registered):
        """Add a plugin

        IN: plugin: str
        IN: state: bool
        IN: path: str
        IN: registered: bool

        OU: bool
        """
        self.plugins[plugin] = {}
        self.plugins[plugin]["enabled"] = state
        self.plugins[plugin]["path"] = path
        self.plugins[plugin]["registered"] = registered

    def remove(self, plugin):
        """
        Remove a Plugin
        """
        self.plugins.pop(plugin)

    def enable(self, plugin):
        """
        Enable a Plugin
        """
        self.plugins[plugin]["enabled"] = True

    def disable(self, plugin):
        """
        Disable a plugin
        """
        self.plugins[plugin]["enabled"] = False

    def toggle(self, plugin):
        """
        Toggle 'enabled' boolean state of a plugin
        """
        self.plugins[plugin]["enabled"] = not self.plugins[plugin]["enabled"]

    def is_enabled(self, plugin):
        """
        True if 'plugin' is enabled
        """
        if plugin not in self.plugins:
            return None

        if self.plugins[plugin]["enabled"] is None:
            return None

        if not self.plugins[plugin]["enabled"]:  # False
            return False
        return True

    def is_disabled(self, plugin):
        """
        True if 'plugin' is disabled
        """
        if plugin not in self.plugins:
            return None

        if self.plugins[plugin]["enabled"] is None:
            return None

        if self.plugins[plugin]["enabled"]:
            return False
        return True

    def ls_enabled(self):
        """
        List enabled plugins
        """
        _enabled = []

        for plugin in self.plugins:
            if self.plugins[plugin]["enabled"]:
                _enabled.append(plugin)

        return _enabled

    def ls_disabled(self):
        """
        List disabled plugins
        """
        _enabled = []

        for plugin in self.plugins:
            if not self.plugins[plugin]["enabled"]:
                _enabled.append(plugin)

        return _enabled

    def ls_all(self):
        """
        List al plugins
        """
        return list(self.plugins)

    def register(self, plugin):
        """
        Register a Plugin
        """
        self.plugins[plugin]["registered"] = True

    def unregister(self, plugin):
        """
        Unregister a plugin
        """
        self.plugins[plugin]["registered"] = False

    def toggle_registered(self, plugin):
        """
        Toggle 'registered' boolean state of a plugin
        """
        self.plugins[plugin]["registered"] = not self.plugins[plugin]["registered"]

    def is_registered(self, plugin):
        """
        True if 'plugin' is registered
        """
        if self.plugins[plugin]["registered"] is None:
            return None

        if not self.plugins[plugin]["registered"]:
            return False
        return True

    def is_unregistered(self, plugin):
        """
        True if 'plugin' is unregistered
        """
        if self.plugins[plugin]["registered"] is None:
            return None

        if self.plugins[plugin]["registered"]:
            return False
        return True

    def ls_registered(self):
        """
        List registered plugins
        """
        _registered = []

        for plugin in self.plugins:
            if self.plugins[plugin]["registered"]:
                _registered.append(plugin)

        return _registered

    def ls_unregistered(self):
        """
        List unregistered plugins
        """
        _registered = []

        for plugin in self.plugins:
            if not self.plugins[plugin]["registered"]:
                _registered.append(plugin)

        return _registered

    def __del__(self):
        """
        Deller
        """
        wdebug("# %s:%s()" % (self.__class__, callee()))

        self.persistence.dump(source_object=self.config)
